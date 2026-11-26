"""Publication fixtures exercise decisions without changing remote state."""

import json
import subprocess
import unittest
from unittest.mock import patch

import publish_release as publication

REVISION = "1" * 40
DIGEST = "sha256:" + "a" * 64
IMAGE = "example/fastapi_img"
REPOSITORY = "example/fastapi"


def artifact(version, revision=REVISION):
    return DIGEST, {
        publication.VERSION_LABEL: version,
        publication.REVISION_LABEL: revision,
    }


class PublicationTests(unittest.TestCase):
    @patch.object(publication, "version_at")
    def test_publish_only_on_numeric_increase(self, version_at):
        version_at.side_effect = [(0, 0, 9), (0, 0, 10)]
        self.assertEqual(publication.release_version("before", "after"), (0, 0, 10))
        version_at.side_effect = [(0, 0, 10), (0, 0, 10)]
        self.assertIsNone(publication.release_version("before", "after"))
        version_at.side_effect = [(0, 0, 10), (0, 0, 9)]
        with self.assertRaisesRegex(ValueError, "decreased"):
            publication.release_version("before", "after")

    def test_promotion_requires_same_repo_and_exact_revision(self):
        pull = {
            "merged_at": "2026-09-21",
            "merge_commit_sha": REVISION,
            "base": {"ref": "stable-main", "repo": {"full_name": REPOSITORY}},
            "head": {"ref": "stable-develop", "repo": {"full_name": REPOSITORY}},
        }
        self.assertTrue(publication.is_promotion(pull, REPOSITORY, REVISION))
        self.assertFalse(publication.is_promotion(pull, REPOSITORY, "2" * 40))
        pull["head"]["repo"]["full_name"] = "fork/fastapi"
        self.assertFalse(publication.is_promotion(pull, REPOSITORY, REVISION))

    @patch.object(publication, "image_metadata", return_value=artifact("0.0.8", "2" * 40))
    def test_conflicting_image_fails_preflight(self, _):
        with self.assertRaisesRegex(ValueError, "belongs to another release"):
            publication.verify_image(IMAGE, "0.0.8", REVISION)

    @patch.object(publication, "tag_revision", return_value="2" * 40)
    def test_conflicting_git_tag_fails_preflight(self, _):
        with self.assertRaisesRegex(ValueError, "another commit"):
            publication.verify_tag("v0.0.8", REVISION)

    @patch.object(publication, "command")
    def test_only_confirmed_missing_image_is_absent(self, command):
        reference = f"{IMAGE}:0.0.8"
        command.return_value = subprocess.CompletedProcess(
            ["docker"], 1, "", f"ERROR: docker.io/{reference}: not found\n"
        )
        self.assertIsNone(publication.image_metadata(reference))
        command.return_value = subprocess.CompletedProcess(
            ["docker"], 1, "", "ERROR: unauthorized: authentication required\n"
        )
        with self.assertRaises(subprocess.CalledProcessError):
            publication.image_metadata(reference)

    @patch.object(publication, "command")
    def test_registry_index_supplies_digest_and_labels(self, command):
        configs = {"linux/amd64": {"config": {"Labels": artifact("0.0.8")[1]}}}
        command.return_value = subprocess.CompletedProcess(
            ["docker"], 0, f"{DIGEST}\n{json.dumps(configs)}\n", ""
        )
        self.assertEqual(publication.image_metadata(f"{IMAGE}:0.0.8"), artifact("0.0.8"))

    @patch.object(publication, "command")
    @patch.object(publication, "image_metadata")
    def test_retry_reuses_image_and_repairs_latest(self, metadata, command):
        legacy_labels = {publication.VERSION_LABEL: "latest", "version": "0.0.7"}
        metadata.side_effect = [artifact("0.0.8"), ("old", legacy_labels)]
        command.return_value = subprocess.CompletedProcess(["docker"], 0, "", "")
        self.assertTrue(publication.promote_image(IMAGE, "0.0.8", REVISION))
        command.assert_called_once_with(
            "docker", "buildx", "imagetools", "create", "--prefer-index=false",
            "--tag", f"{IMAGE}:latest", f"{IMAGE}@{DIGEST}",
        )
        command.reset_mock()
        metadata.side_effect = [artifact("0.0.8"), artifact("0.0.8")]
        self.assertTrue(publication.promote_image(IMAGE, "0.0.8", REVISION))
        command.assert_not_called()

    @patch.object(publication, "command")
    @patch.object(publication, "image_metadata")
    def test_outdated_retry_leaves_newer_latest_and_description(self, metadata, command):
        metadata.side_effect = [artifact("0.0.8"), artifact("0.0.10")]
        self.assertFalse(publication.promote_image(IMAGE, "0.0.8", REVISION))
        command.assert_not_called()

    @patch.object(publication, "command")
    @patch.object(publication, "verify_tag", return_value=True)
    def test_retry_reuses_tag_and_creates_only_missing_release(self, _, command):
        command.side_effect = [
            subprocess.CompletedProcess(["gh"], 1, "", "release not found"),
            subprocess.CompletedProcess(["gh"], 0, "", ""),
        ]
        publication.publish_github(REPOSITORY, "v0.0.8", REVISION, latest=False)
        self.assertEqual(command.call_count, 2)
        self.assertIn("--verify-tag", command.call_args.args)
        self.assertIn("--latest=false", command.call_args.args)

    @patch.object(publication, "command")
    @patch.object(publication, "verify_tag", return_value=True)
    def test_completed_release_does_not_publish_twice(self, _, command):
        command.return_value = subprocess.CompletedProcess(["gh"], 0, '{"isDraft": false}', "")
        publication.publish_github(REPOSITORY, "v0.0.8", REVISION, latest=True)
        command.assert_called_once_with(
            "gh", "release", "view", "v0.0.8", "--repo", REPOSITORY, "--json", "isDraft"
        )


if __name__ == "__main__":
    unittest.main()

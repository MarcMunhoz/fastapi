from contextlib import chdir
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from release_metadata import Commit, check_release_files, commits_between, next_version, render_metadata


BASE_FILES = {
    "app/pyproject.toml": '[tool.poetry]\nversion = "0.0.7"\n',
    "README.md": "Current version: `0.0.7`\n",
    "README-DKHUB.md": (
        "docker pull example/fastapi_img:0.0.7\n"
        "docker run -p 8000:8000 example/fastapi_img:0.0.7\n"
        "- `0.0.7`: current semantic version\n"
        "Prefer versioned tags such as `0.0.7` for reproducibility.\n"
        "FROM example/fastapi_img:0.0.7\n"
        "Historical: `0.0.7`\n"
    ),
    "Dockerfile": '  version="0.0.7" \\\n',
    "CHANGELOG.md": "# Changelog\n\n## 2026-09-21\n\n### [v0.0.7]\n\n- Historical.\n",
}


def commit(subject, body=""):
    return Commit(subject, body, "2026-11-26")


class ReleaseMetadataTests(unittest.TestCase):
    def test_chooses_strongest_conventional_commit(self):
        base = (0, 0, 7)
        for messages, expected in [
            (["docs: Clarifies usage", "chore(release): Synchronizes version metadata"], base),
            (["fix(api): Handles empty requests"], (0, 0, 8)),
            (["perf(api): Reduces latency"], (0, 0, 8)),
            (["fix: Corrects a bug", "feat(api): Adds endpoint"], (0, 1, 0)),
            (["feat: Adds endpoint", "refactor!: Removes an endpoint"], (1, 0, 0)),
        ]:
            with self.subTest(messages=messages):
                self.assertEqual(next_version(base, [commit(message) for message in messages]), expected)
        self.assertEqual(next_version(base, [commit("refactor: Changes API", "BREAKING CHANGE: old API removed")]), (1, 0, 0))

    def test_updates_current_metadata_and_preserves_history(self):
        commits = [commit("fix(api): Handles empty requests")]
        actual = render_metadata(BASE_FILES, BASE_FILES, commits)
        self.assertIn('version = "0.0.8"', actual["app/pyproject.toml"])
        self.assertIn("Current version: `0.0.8`", actual["README.md"])
        self.assertEqual(actual["README-DKHUB.md"].count("0.0.8"), 5)
        self.assertIn("Historical: `0.0.7`", actual["README-DKHUB.md"])
        self.assertIn('version="0.0.8"', actual["Dockerfile"])
        self.assertIn("### [v0.0.8]", actual["CHANGELOG.md"])
        self.assertIn("- Handles empty requests", actual["CHANGELOG.md"])
        self.assertIn("### [v0.0.7]", actual["CHANGELOG.md"])
        self.assertEqual(render_metadata(BASE_FILES, actual, commits), actual)

    def test_recalculating_a_pending_release_replaces_its_draft_entry(self):
        commits = [commit("fix: Corrects a bug")]
        draft = render_metadata(BASE_FILES, BASE_FILES, commits)
        revised = render_metadata(BASE_FILES, draft, [*commits, commit("feat: Adds an endpoint")])
        self.assertNotIn("### [v0.0.8]", revised["CHANGELOG.md"])
        self.assertIn("### [v0.1.0]", revised["CHANGELOG.md"])
        self.assertIn("### [v0.0.7]", revised["CHANGELOG.md"])

    def test_published_entries_remain_when_preparing_the_next_release(self):
        published = render_metadata(BASE_FILES, BASE_FILES, [commit("fix: Corrects a bug")])
        actual = render_metadata(published, published, [commit("feat: Adds an endpoint")])
        self.assertIn("### [v0.0.8]", actual["CHANGELOG.md"])
        self.assertIn("### [v0.1.0]", actual["CHANGELOG.md"])

    def test_squashed_release_is_excluded_only_if_the_published_section_matches(self):
        published = render_metadata(BASE_FILES, BASE_FILES, [commit("fix: Corrects a bug")])
        base = "target"
        head = "source"
        generated = "generated"
        for generated_changelog, excludes_commit in [
            (published["CHANGELOG.md"], True),
            (published["CHANGELOG.md"].replace("Corrects a bug", "Fixes something else"), False),
        ]:
            with self.subTest(excludes_commit=excludes_commit):
                def git(*args):
                    if args[0] == "show":
                        path = args[1].split(":", 1)[1]
                        return generated_changelog if path == "CHANGELOG.md" else published[path]
                    if "--format=%H%x00%s" in args:
                        return generated + "\0chore(release): Synchronizes version metadata\n"
                    if "^generated" in args:
                        return "feat: Adds endpoint\0\x002026-11-26\0"
                    return "fix: Corrects a bug\0\x002026-11-26\0"

                with patch("release_metadata.git", side_effect=git):
                    commits = commits_between(base, head, (0, 0, 8), published["CHANGELOG.md"])
                    self.assertEqual(commits[0].subject.startswith("feat:"), excludes_commit)

    def test_tooling_changes_do_not_write_release_metadata(self):
        self.assertEqual(render_metadata(BASE_FILES, BASE_FILES, [commit("ci: Updates workflow")]), BASE_FILES)

    def test_decreased_versions_are_rejected(self):
        files = dict(BASE_FILES, **{"app/pyproject.toml": '[tool.poetry]\nversion = "0.0.6"\n'})
        with self.assertRaisesRegex(ValueError, "older than"):
            render_metadata(BASE_FILES, files, [])

    def test_invalid_versions_are_rejected(self):
        files = dict(BASE_FILES, **{"app/pyproject.toml": '[tool.poetry]\nversion = "0.00.7"\n'})
        with self.assertRaisesRegex(ValueError, "stable SemVer"):
            render_metadata(BASE_FILES, files, [])

    def test_published_metadata_checks_current_references_and_changelog(self):
        with TemporaryDirectory() as directory, chdir(directory):
            Path("app").mkdir()
            for name, content in BASE_FILES.items():
                Path(name).write_text(content, encoding="utf-8")

            check_release_files((0, 0, 7))
            Path("README.md").write_text("Current version: `0.0.6`\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "README.md: expected version 0.0.7"):
                check_release_files((0, 0, 7))

            Path("README.md").write_text(BASE_FILES["README.md"], encoding="utf-8")
            Path("CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "CHANGELOG.md: missing"):
                check_release_files((0, 0, 7))


if __name__ == "__main__":
    unittest.main()

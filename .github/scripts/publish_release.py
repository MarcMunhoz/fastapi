"""Plan and resume publication of a single integrated release."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import time

from release_metadata import check_release_files, format_version, parse_version, version_at

VERSION_LABEL = "org.opencontainers.image.version"
REVISION_LABEL = "org.opencontainers.image.revision"


def command(*args):
    return subprocess.run(args, capture_output=True, text=True, check=False)


def checked_output(result):
    result.check_returncode()
    return result.stdout.strip()


def release_version(before, after):
    previous = version_at(before)
    version = version_at(after)
    if version < previous:
        raise ValueError("The integrated release version decreased.")
    return version if version > previous else None


def is_promotion(pull, repository, revision):
    base = pull.get("base") or {}
    head = pull.get("head") or {}
    return (
        pull.get("merged_at")
        and pull.get("merge_commit_sha") == revision
        and base.get("ref") == "stable-main"
        and head.get("ref") == "stable-develop"
        and all(
            (branch.get("repo") or {}).get("full_name", "").lower() == repository.lower()
            for branch in (base, head)
        )
    )


def verify_promotion(repository, revision):
    endpoint = f"repos/{repository}/commits/{revision}/pulls"
    # Commit association can briefly lag behind the push event.
    for delay in (0, 2, 4, 8, 16):
        if delay:
            time.sleep(delay)
        pages = json.loads(checked_output(command("gh", "api", "--paginate", "--slurp", endpoint)))
        if any(is_promotion(pull, repository, revision) for page in pages for pull in page):
            return
    raise ValueError("The release commit was not introduced by a same-repository promotion PR.")


def tag_revision(tag):
    ref = f"refs/tags/{tag}"
    result = command("git", "ls-remote", "--exit-code", "origin", ref, f"{ref}^{{}}")
    if result.returncode == 2:
        return None
    refs = dict(line.split("\t", 1)[::-1] for line in checked_output(result).splitlines())
    return refs.get(f"{ref}^{{}}") or refs[ref]


def verify_tag(tag, revision):
    target = tag_revision(tag)
    if target and target != revision:
        raise ValueError(f"Git tag {tag} already identifies another commit.")
    return bool(target)


def image_metadata(reference):
    result = command(
        "docker", "buildx", "imagetools", "inspect",
        "--format", "{{.Manifest.Digest}}\n{{json .Image}}", reference,
    )
    if result.returncode:
        if any(
            line.strip().removeprefix("ERROR: ") in {
                f"{prefix}{reference}: {message}"
                for prefix in ("", "docker.io/", "registry-1.docker.io/")
                for message in ("not found", "manifest unknown")
            }
            for line in result.stderr.splitlines()
        ):
            return None
        result.check_returncode()
    digest, raw_config = result.stdout.split("\n", 1)
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        raise ValueError("The registry returned an invalid image digest.")
    config = json.loads(raw_config)
    config = config.get("linux/amd64", config)
    labels = config.get("config", {}).get("Labels") or {}
    return digest, labels


def verify_image(image, version, revision):
    existing = image_metadata(f"{image}:{version}")
    if existing is None:
        return None
    digest, labels = existing
    if labels.get(VERSION_LABEL) != version or labels.get(REVISION_LABEL) != revision:
        raise ValueError(f"Docker image tag {version} belongs to another release.")
    return digest


def may_update_latest(latest, version, revision):
    if latest is None:
        return True
    _, labels = latest
    current = labels.get(VERSION_LABEL)
    if current in (None, "", "latest"):
        # The old metadata action could pick the moving tag as its OCI version.
        current = labels.get("version", "")
    try:
        current_parts = parse_version(current)
    except ValueError as error:
        raise ValueError("Cannot determine the version currently published as latest.") from error
    desired_parts = parse_version(version)
    if current_parts == desired_parts and labels.get(REVISION_LABEL) != revision:
        raise ValueError("Docker latest identifies another commit with the same version.")
    return current_parts <= desired_parts


def promote_image(image, version, revision):
    digest = verify_image(image, version, revision)
    if digest is None:
        raise ValueError("The versioned image is unavailable after publication.")
    latest = image_metadata(f"{image}:latest")
    if not may_update_latest(latest, version, revision):
        return False
    if latest is None or latest[0] != digest:
        checked_output(command(
            "docker", "buildx", "imagetools", "create", "--prefer-index=false",
            "--tag", f"{image}:latest", f"{image}@{digest}",
        ))
    return True


def publish_github(repository, tag, revision, latest):
    if not verify_tag(tag, revision):
        checked_output(command(
            "gh", "api", "--method", "POST", f"repos/{repository}/git/refs",
            "-f", f"ref=refs/tags/{tag}", "-f", f"sha={revision}",
        ))
    release = command("gh", "release", "view", tag, "--repo", repository, "--json", "isDraft")
    if release.returncode == 0:
        if json.loads(release.stdout)["isDraft"]:
            raise ValueError(f"GitHub release {tag} already exists as a draft.")
        return
    checked_output(command(
        "gh", "release", "create", tag, "--repo", repository,
        "--verify-tag", "--generate-notes", "--title", tag,
        "--latest" if latest else "--latest=false",
    ))


def write_output(name, value):
    with Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as output:
        output.write(f"{name}={value}\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("plan", "preflight", "promote-image", "publish-github"))
    stage = parser.parse_args().stage
    revision = os.environ["GITHUB_SHA"]
    repository = os.environ["GITHUB_REPOSITORY"]
    if stage == "plan":
        version = release_version(os.environ["BEFORE_SHA"], revision)
        if version is not None:
            check_release_files(version)
            verify_promotion(repository, revision)
            write_output("version", format_version(version))
        return

    version = os.environ["APP_VERSION"]
    tag = f"v{version}"
    if stage == "publish-github":
        publish_github(repository, tag, revision, os.environ["LATEST"] == "true")
        return
    image = os.environ["IMAGE_NAME"]
    if stage == "preflight":
        verify_tag(tag, revision)
        exists = verify_image(image, version, revision) is not None
        write_output("image_exists", str(exists).lower())
    elif stage == "promote-image":
        is_latest = promote_image(image, version, revision)
        write_output("latest", str(is_latest).lower())


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error)) from error

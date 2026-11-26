"""Calculate, prepare, and check the metadata for a promotion."""

import argparse
from dataclasses import dataclass
from html import escape
from pathlib import Path
import re
import subprocess
import sys
import tomllib


MANIFEST = "app/pyproject.toml"
CHANGELOG = "CHANGELOG.md"
VERSION_PATTERN = r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
GENERATED_SUBJECT = "chore(release): Synchronizes version metadata"
CONVENTIONAL = re.compile(r"^(?P<type>[a-z]+)(?:\([^()]+\))?(?P<breaking>!)?: (?P<description>.+)$")
BREAKING_FOOTER = re.compile(r"^BREAKING[ -]CHANGE: \S", re.MULTILINE)
IMAGE = r"[\w./-]+/fastapi_img:"
VERSION_MARKERS = {
    MANIFEST: [r'^version\s*=\s*"(?P<version>[^"\n]+)"\s*$'],
    "README.md": [r"^Current version: `(?P<version>[^`\n]+)`$"],
    "README-DKHUB.md": [
        rf"^docker pull {IMAGE}(?P<version>\S+)$",
        rf"^docker run -p 8000:8000 {IMAGE}(?P<version>\S+)$",
        rf"^FROM {IMAGE}(?P<version>\S+)$",
        r"^- `(?P<version>[^`\n]+)`: current semantic version$",
        r"^Prefer versioned tags such as `(?P<version>[^`\n]+)` ",
    ],
    "Dockerfile": [r'^  version="(?P<version>[^"\n]+)" \\$'],
}
GENERATED_SECTION = re.compile(
    rf"^<!-- release-metadata: (?P<version>{VERSION_PATTERN}) -->\n"
    r".*?^<!-- /release-metadata -->\n\n",
    re.MULTILINE | re.DOTALL,
)
BUMP_CATEGORY = {1: "Fixed", 2: "Added", 3: "Breaking Changes"}
Version = tuple[int, int, int]


@dataclass(frozen=True)
class Commit:
    subject: str
    body: str
    date: str


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True, encoding="utf-8")


def parse_version(value: str) -> Version:
    if not re.fullmatch(VERSION_PATTERN, value):
        raise ValueError(f"{MANIFEST}: a stable SemVer (MAJOR.MINOR.PATCH) is required")
    major, minor, patch = map(int, value.split("."))
    return major, minor, patch


def format_version(version: Version) -> str:
    return ".".join(map(str, version))


def manifest_version(content: str) -> Version:
    value = tomllib.loads(content).get("tool", {}).get("poetry", {}).get("version")
    if not isinstance(value, str):
        raise ValueError(f"{MANIFEST}: missing tool.poetry.version")
    return parse_version(value)


def version_at(revision: str) -> Version:
    return manifest_version(git("show", f"{revision}:{MANIFEST}"))


def generated_section(changelog: str, version: Version) -> str | None:
    for section in GENERATED_SECTION.finditer(changelog):
        if section["version"] == format_version(version):
            return section[0]
    return None


def commits_between(base: str, head: str, version: Version, changelog: str) -> list[Commit]:
    revisions = [f"{base}..{head}"]
    published_section = generated_section(changelog, version)
    if published_section:
        candidates = git("log", "--no-merges", "--format=%H%x00%s", *revisions)
        for candidate in candidates.splitlines():
            revision, _, subject = candidate.partition("\0")
            if subject == GENERATED_SUBJECT and version_at(revision) == version:
                source_changelog = git("show", f"{revision}:{CHANGELOG}")
                if generated_section(source_changelog, version) == published_section:
                    # Squash and rebase change commit IDs while retaining the generated release.
                    revisions.append(f"^{revision}")
                    break
    records = git("log", "--no-merges", "-z", "--format=%s%x00%b%x00%cs", *revisions)
    if not records:
        return []
    fields = records.removesuffix("\0").split("\0")
    return [Commit(*fields[index:index + 3]) for index in range(0, len(fields), 3)]


def release_changes(commits: list[Commit]) -> list[tuple[int, str, str]]:
    changes = []
    for commit in commits:
        match = CONVENTIONAL.fullmatch(commit.subject)
        if not match or commit.subject == GENERATED_SUBJECT:
            continue
        if match["breaking"] or BREAKING_FOOTER.search(commit.body):
            bump = 3
        else:
            bump = {"fix": 1, "perf": 1, "feat": 2}.get(match["type"], 0)
        if bump:
            changes.append((bump, match["description"], commit.date))
    return changes


def bump_version(base: Version, level: int) -> Version:
    major, minor, patch = base
    return (base, (major, minor, patch + 1), (major, minor + 1, 0), (major + 1, 0, 0))[level]


def next_version(base: Version, commits: list[Commit]) -> Version:
    return bump_version(base, max((level for level, _, _ in release_changes(commits)), default=0))


def update_markers(content: str, path: str, version: Version) -> str:
    for marker in VERSION_MARKERS[path]:
        matches = list(re.finditer(marker, content, re.MULTILINE))
        if len(matches) != 1:
            raise ValueError(f"{path}: expected one current-version marker matching {marker}")
        start, end = matches[0].span("version")
        content = content[:start] + format_version(version) + content[end:]
    return content


def changelog_heading(version: Version) -> str:
    return f"### [v{format_version(version)}]"


def changelog_has_version(changelog: str, version: Version) -> bool:
    return changelog_heading(version) in changelog.splitlines()


def render_changelog(
    base_changelog: str,
    changelog: str,
    version: Version,
    changes: list[tuple[int, str, str]],
) -> str:
    def preserve_published(match: re.Match[str]) -> str:
        existing_version = parse_version(match["version"])
        return match[0] if changelog_has_version(base_changelog, existing_version) else ""

    changelog = GENERATED_SECTION.sub(preserve_published, changelog)
    if not changes:
        return changelog
    if changelog_has_version(changelog, version):
        raise ValueError(f"{CHANGELOG}: version {format_version(version)} already has a release entry")

    date = max(date for _, _, date in changes)
    lines = [
        f"<!-- release-metadata: {format_version(version)} -->",
        f"## {date}",
        "",
        changelog_heading(version),
        "",
    ]
    for level, title in reversed(BUMP_CATEGORY.items()):
        summaries = [escape(description) for bump, description, _ in changes if bump == level]
        if summaries:
            lines.extend([f"#### {title}", *(f"- {summary}" for summary in summaries), ""])
    lines.extend(["<!-- /release-metadata -->", "", ""])
    first_section = re.search(r"^## ", changelog, re.MULTILINE)
    start = first_section.start() if first_section else len(changelog)
    if start:
        # Put the new section ahead of any existing generated section's marker.
        marker = re.search(r"^<!-- release-metadata: [^\n]+ -->\n\Z", changelog[:start], re.MULTILINE)
        if marker:
            start = marker.start()
    return changelog[:start].rstrip() + "\n\n" + "\n".join(lines) + changelog[start:]


def render_metadata(
    base_files: dict[str, str], files: dict[str, str], commits: list[Commit]
) -> dict[str, str]:
    base = manifest_version(base_files[MANIFEST])
    if manifest_version(files[MANIFEST]) < base:
        raise ValueError(f"{MANIFEST}: promotion version is older than {format_version(base)}")
    version = next_version(base, commits)
    result = {path: update_markers(files[path], path, version) for path in VERSION_MARKERS}
    result[CHANGELOG] = render_changelog(
        base_files[CHANGELOG], files[CHANGELOG], version, release_changes(commits)
    )
    return result


def check_release_files(version: Version, changelog_required: bool = True) -> None:
    for path in VERSION_MARKERS:
        content = Path(path).read_text(encoding="utf-8")
        if update_markers(content, path, version) != content:
            raise ValueError(f"{path}: expected version {format_version(version)}")
    if changelog_required:
        changelog = Path(CHANGELOG).read_text(encoding="utf-8")
        if not changelog_has_version(changelog, version):
            raise ValueError(f"{CHANGELOG}: missing {changelog_heading(version)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("prepare", "check"))
    parser.add_argument("base")
    parser.add_argument("head")
    args = parser.parse_args()

    try:
        base_files = {path: git("show", f"{args.base}:{path}") for path in (MANIFEST, CHANGELOG)}
        files = {path: Path(path).read_text(encoding="utf-8") for path in (*VERSION_MARKERS, CHANGELOG)}
        commits = commits_between(
            args.base, args.head, manifest_version(base_files[MANIFEST]), base_files[CHANGELOG]
        )
        expected = render_metadata(base_files, files, commits)
        changed_paths = [path for path in files if files[path] != expected[path]]
        if args.operation == "check" and changed_paths:
            raise ValueError("release metadata differs in " + ", ".join(changed_paths))
        for path in changed_paths:
            Path(path).write_text(expected[path], encoding="utf-8")
        print(format_version(manifest_version(expected[MANIFEST])))
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f"Release metadata: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

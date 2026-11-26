"""Check promotion orchestration without changing a Git repository."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("prepare_promotion.sh").resolve()


class PromotionTest(unittest.TestCase):
    def run_promotion(self, mode):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stub = """#!/usr/bin/env bash
set -eu
command=${0##*/}
printf '%s %s\\n' "$command" "$*" >> "$CALLS"
if [[ "$command" == git ]]; then
    case "$1" in
        rev-parse)
            if [[ -e "$COMMITTED" ]]; then echo prepared; else echo head; fi
            ;;
        ls-remote)
            if [[ "$MODE" == advanced && -e "$COMMITTED" ]]; then
                echo 'new-head refs/heads/stable-develop'
            else
                echo 'head refs/heads/stable-develop'
            fi
            echo 'base refs/heads/stable-main'
            ;;
        -c) touch "$COMMITTED" ;;
        merge-tree) echo merged-tree ;;
        diff)
            if [[ "$2" == --cached && "$MODE" != unchanged ]]; then exit 1; fi
            ;;
    esac
fi
"""
            for command in ("git", "gh", "python3"):
                executable = root / command
                executable.write_text(stub)
                executable.chmod(0o755)
            env = dict(
                os.environ,
                PATH=f"{root}:{os.environ['PATH']}",
                MODE=mode,
                CALLS=str(root / "calls"),
                COMMITTED=str(root / "committed"),
                BASE_SHA="base",
                HEAD_SHA="head",
                GITHUB_REPOSITORY="owner/repo",
                GITHUB_SERVER_URL="https://github.example",
                GITHUB_RUN_ID="123",
            )
            result = subprocess.run(
                ["bash", SCRIPT], cwd=root, env=env, capture_output=True, text=True
            )
            return result, (root / "calls").read_text()

    def test_validates_generated_commit_before_pushing(self):
        result, calls = self.run_promotion("changed")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertLess(calls.index("check base prepared"), calls.index("git push"))
        self.assertIn("git push origin HEAD:refs/heads/stable-develop", calls)
        self.assertIn("repos/owner/repo/statuses/prepared", calls)

    def test_skips_push_when_metadata_is_unchanged(self):
        result, calls = self.run_promotion("unchanged")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("check base head", calls)
        self.assertNotIn("git push", calls)

    def test_stops_when_source_branch_advances(self):
        result, calls = self.run_promotion("advanced")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source or target advanced", result.stderr)
        self.assertNotIn("git push", calls)


if __name__ == "__main__":
    unittest.main()

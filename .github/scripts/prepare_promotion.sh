#!/usr/bin/env bash
set -euo pipefail

source_ref=refs/heads/stable-develop
target_ref=refs/heads/stable-main
metadata_files=(app/pyproject.toml README.md README-DKHUB.md Dockerfile CHANGELOG.md)

check_refs() {
    local refs
    refs=$(git ls-remote --refs origin "$source_ref" "$target_ref")
    if [[ "$(awk -v ref="$source_ref" '$2 == ref {print $1}' <<< "$refs")" != "$HEAD_SHA" ||
          "$(awk -v ref="$target_ref" '$2 == ref {print $1}' <<< "$refs")" != "$BASE_SHA" ]]; then
        echo 'The promotion source or target advanced while preparing the release.' >&2
        exit 1
    fi
}

check_promotion() {
    local revision=$1
    local merged_tree
    python3 -B .github/scripts/release_metadata.py check "$BASE_SHA" "$revision"
    merged_tree=$(git merge-tree --write-tree "$BASE_SHA" "$revision")
    if ! git diff --quiet "$revision" "$merged_tree" -- "${metadata_files[@]}"; then
        echo 'The merged result would change the prepared release metadata.' >&2
        exit 1
    fi
}

if [[ "$(git rev-parse HEAD)" != "$HEAD_SHA" ]]; then
    echo 'The checkout does not match the promotion source.' >&2
    exit 1
fi

check_refs
python3 -B .github/scripts/release_metadata.py prepare "$BASE_SHA" "$HEAD_SHA"
git add -- "${metadata_files[@]}"

if git diff --cached --quiet; then
    check_promotion "$HEAD_SHA"
    check_refs
    exit 0
fi

git -c user.name='github-actions[bot]' \
    -c user.email='41898282+github-actions[bot]@users.noreply.github.com' \
    commit -m 'chore(release): Synchronizes version metadata'

prepared_sha=$(git rev-parse HEAD)
check_promotion "$prepared_sha"
check_refs
git push origin "HEAD:$source_ref"

# A push authenticated with GITHUB_TOKEN does not start a new PR workflow.
# Record the checks on the exact generated revision that was validated above.
gh api --method POST "repos/$GITHUB_REPOSITORY/statuses/$prepared_sha" \
    -f state=success -f context='Release quality / prepare' \
    -f description='Generated release metadata passed validation.' \
    -f target_url="$GITHUB_SERVER_URL/$GITHUB_REPOSITORY/actions/runs/$GITHUB_RUN_ID" >/dev/null

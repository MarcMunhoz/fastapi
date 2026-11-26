## 1. Version preparation and validation

- [x] 1.1 Implement SemVer calculation from the target version and Conventional Commits, excluding generated metadata commits.
- [x] 1.2 Generate and synchronize the Poetry version, both READMEs, the Dockerfile version label, and the changelog from the calculated release.
- [x] 1.3 Apply the generated release metadata on the existing source branch for same-repository promotion PRs and verify the resulting revision with read-only checks.

## 2. Release publication

- [x] 2.1 Detect version increases on integration and skip publication for unchanged versions.
- [x] 2.2 Publish the versioned Docker image and update Docker Hub moving references with revision checks, serialization, and stale-run protection.
- [x] 2.3 Publish the matching Git tag and GitHub Release with conflict detection and safe retry behavior.

## 3. Verification

- [x] 3.1 Verify automatic major, minor, and patch selection, unchanged versions, README and changelog generation, idempotent reruns, source branch advancement, and rejection of inconsistent metadata.
- [x] 3.2 Verify publication decisions for unchanged and increased versions, partial publication retries, conflicting artifacts, and stale runs using controlled fixtures.

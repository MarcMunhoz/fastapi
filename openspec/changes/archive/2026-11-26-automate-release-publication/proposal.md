## Why

The Docker workflow can republish an existing version after a merge, and release metadata is maintained by hand across multiple files. Validating release inputs and automating publication will keep the published image, GitHub release, and displayed version aligned.

## What Changes

- Calculate the next version automatically from the changes in the promotion PR, then update `app/pyproject.toml`, both READMEs, Docker image metadata, and the changelog.
- Validate release metadata and the changelog on promotion PRs from `stable-develop` to `stable-main`.
- Publish the versioned Docker image, Git tag, and GitHub Release only when the integrated version increases. Make publication retryable without overwriting an existing versioned artifact.

## Capabilities

### New Capabilities

- `release-publication` covers version preparation, promotion validation, and publication to Docker Hub and GitHub.

### Modified Capabilities

## Impact

The change affects release scripts, GitHub Actions, version references in documentation and the Docker image, and the release process for maintainers.

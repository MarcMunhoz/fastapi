## ADDED Requirements

### Requirement: Promotion automatically prepares release metadata

The promotion workflow SHALL calculate the next SemVer from the target version and the strongest Conventional Commit signal in the promotion range. Breaking changes require a major bump, features a minor bump, and fixes or performance improvements a patch bump. The workflow SHALL ignore its generated metadata commits when calculating the next version.

#### Scenario: A promotion contains release-relevant changes
- **WHEN** the same-repository promotion PR contains commits that require a bump
- **THEN** automation calculates the version, updates `app/pyproject.toml`, the displayed version in `README.md`, the current image references in `README-DKHUB.md`, and the Dockerfile version label
- **AND** it generates the matching changelog entry from release-relevant commits and records the changes together on the existing source branch

#### Scenario: A promotion has only tooling or documentation changes
- **WHEN** the promotion has no commit requiring a bump
- **THEN** automation keeps the existing version and generates no release entry

#### Scenario: Preparation is repeated
- **WHEN** the workflow runs again with the same promotion inputs and synchronized metadata
- **THEN** the workflow produces no additional commit

### Requirement: Promotion validates release inputs

The promotion check SHALL compare the effective release version with the target branch and reject invalid versions, decreases, deviations from the calculated version, stale version references, and increases without a matching generated changelog entry.

#### Scenario: Release metadata is incomplete
- **WHEN** a promotion contains an invalid, decreased, or unexpected version, stale version references, or a version increase without a matching entry in `CHANGELOG.md`
- **THEN** the check fails and identifies the affected version or file without modifying the PR

#### Scenario: A promotion keeps the existing version
- **WHEN** a promotion keeps the target version and the version references are synchronized
- **THEN** the release check passes and publication is skipped

### Requirement: A version increase publishes matching release artifacts

The publication workflow SHALL publish the versioned Docker image, update the Docker Hub description and `latest`, and publish a Git tag and GitHub Release for a version increase integrated into `stable-main`.

#### Scenario: An increased version is integrated
- **WHEN** a promotion with a validated version increase is integrated from `stable-develop`
- **THEN** the published image and Git tag identify the integrated commit and the GitHub Release uses that tag

#### Scenario: A promotion keeps the existing version
- **WHEN** an integrated promotion has the same release version as the prior target state
- **THEN** no image, Docker Hub description, Git tag, or GitHub Release is published

### Requirement: Publication can resume without replacing existing versioned artifacts

The publication workflow SHALL reuse artifacts already associated with the version and integrated commit, publish missing artifacts, and fail on conflicting versioned artifacts.

#### Scenario: Publication is retried after partial success
- **WHEN** the workflow is retried and only some artifacts exist for the integrated commit
- **THEN** it publishes the missing artifacts and leaves existing matching versioned artifacts intact

#### Scenario: A versioned artifact belongs to another commit
- **WHEN** an existing versioned Docker image or Git tag conflicts with the integrated commit
- **THEN** publication fails without overwriting the conflicting artifact

#### Scenario: An older publication is retried
- **WHEN** a newer version has already been published and an older run resumes
- **THEN** the older run leaves `latest` and the current Docker Hub description on the newer version

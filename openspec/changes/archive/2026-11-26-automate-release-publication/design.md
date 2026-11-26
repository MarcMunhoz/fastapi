## Context

The Docker workflow publishes after a promotion merge and reads the version from Poetry metadata. The current version also appears in the GitHub README, the Docker Hub README, and the Dockerfile.

## Goals / Non-Goals

- Prepare the version, changelog, and current-version references automatically on the existing promotion branch.
- Validate promotions and publish GitHub and Docker Hub artifacts from the same integrated commit.

## Decisions

- Calculate the next SemVer from the target branch version and the strongest Conventional Commit signal in the promotion range. A breaking change produces a major bump, a feature a minor bump, and a fix or performance improvement a patch bump. Tooling and documentation changes alone keep the existing version. Exclude automation-generated metadata commits from the calculation.
- Automatically update `app/pyproject.toml`, the `Current version` line in `README.md`, the current-tag references in `README-DKHUB.md`, and the Dockerfile version label. Generate the matching changelog section from release-relevant commit summaries and preserve historical sections. Write all updates in one automation commit on the existing `stable-develop` branch for same-repository promotion PRs. Validate the input revision before writing, use a non-forced push, and stop if the source branch advances. A rerun for the same inputs produces no additional commit. Run the PR checks against the resulting revision so publication uses the same metadata.
- Run the same metadata rules in read-only mode on the prospective promotion result before publication. Compare the version against the target branch using SemVer precedence. Require the calculated version and its generated changelog heading for an increase. Equal versions can pass for changes that do not need publication.
- Use the integrated commit and the prior target state to decide if publication is due. Sequence the Docker image and documentation, Git tag, and GitHub Release so each step can resume from artifacts already published for the same version and revision. Keep credentials in the publication workflow.
- Serialize publication and verify that an older run cannot move `latest` or the Docker Hub description behind a newer release. Check existing versioned image metadata and Git tag targets before proceeding. Treat a mismatched revision as a conflict and report the affected artifact.

## Risks / Trade-offs

- Merge history and reruns can cause stale publication decisions. Use explicit revisions and verify the current destination state before updating moving references.
- The existing source-branch rules require pull requests. The preparation workflow accepts `RELEASE_PREPARATION_TOKEN` for an automation identity already permitted to update that branch. The workflow reports a rejected push as a failure.
- A partial failure can leave the image published before the GitHub Release exists. Resume missing actions and reuse matching versioned artifacts.

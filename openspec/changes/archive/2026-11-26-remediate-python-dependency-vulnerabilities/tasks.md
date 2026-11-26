## 1. Baseline and inventory

- [x] 1.1 Install the baseline lockfile in the project container and collect pip-audit results.
- [x] 1.2 Reconcile the current Dependabot and pip-audit findings and map the affected lockfile paths and dependency groups.

## 2. Dependency remediation

- [x] 2.1 Resolve patched versions of the affected dependency chains, including the filelock major upgrade.
- [x] 2.2 Evaluate compatible updates to direct dependencies and regenerate the Poetry lockfile in the container.

## 3. Verification

- [x] 3.1 Verify the final lockfile with a clean container installation and compare the final audit with the baseline.
- [x] 3.2 Run Ruff and pytest, build and inspect the production image, and smoke-test the root and health endpoints.
- [x] 3.3 Record the resulting versions, validation evidence, and any residual findings in the security inventory.

## Why

The Poetry lockfile has 14 open Dependabot alerts across four packages, including a critical certifi advisory. [Issue #12](https://github.com/MarcMunhoz/fastapi/issues/12) tracks the security and dependency maintenance round on `issue_12`.

## What Changes

- Reconcile Dependabot and containerized pip-audit findings in a security inventory.
- Remediate vulnerable dependency paths and evaluate compatible updates to direct dependencies.
- Verify the final development and production dependency graphs and preserve API behavior.

## Capabilities

### New Capabilities

### Modified Capabilities

- `dependency-security` expands the existing requirements to cover the current advisory inventory and compatible updates.

## Impact

The work affects the Poetry dependencies and lockfile and their validation in the project containers.

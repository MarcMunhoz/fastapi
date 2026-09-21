## 1. Resolve Vulnerable Dependencies

- [x] 1.1 Run a targeted Poetry update for `anyio`, `starlette`, `pip`, and `msgpack` inside the project container.
- [x] 1.2 If resolution fails, update only the direct parent constraint that blocks a fixed transitive version and document the resolver evidence.
- [x] 1.3 Review the complete lockfile diff and remove any unrelated dependency churn that is not required by resolution.
- [x] 1.4 Confirm the lockfile records `anyio` 4.14.2 or newer, `starlette` 1.3.1 or newer, `pip` 26.2.0 or newer, and `msgpack` 1.2.1 or newer.
- [x] 1.5 Confirm Starlette and AnyIO remain in the main group while pip and msgpack remain development-only dependencies.
- [x] 1.6 Update `idna` to version 3.15 or newer after reproducing `PYSEC-2026-215` in the container audit.

## 2. Validate the Remediated Graph

- [x] 2.1 Run Poetry metadata validation inside the project container.
- [x] 2.2 Audit the resolved development graph inside the project container and confirm that all six original advisory identifiers are absent.
- [x] 2.3 Run the applicable application checks inside the project container and verify the root and health endpoints retain their existing behavior.
- [x] 2.4 Build the development and production container targets from the updated lockfile and confirm the production target excludes development-only packages.

## 3. Verify Repository Remediation

- [x] 3.1 Review the final dependency metadata diff and record the resolved versions and validation evidence.
- [x] 3.2 After the dependency update is pushed, confirm that GitHub closes Dependabot alerts 6 through 11 without dismissing them manually.

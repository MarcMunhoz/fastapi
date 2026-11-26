## Context

[Issue #12](https://github.com/MarcMunhoz/fastapi/issues/12) coordinates the maintenance work on `issue_12`. The initial Dependabot report identifies 14 alerts. The current Poetry lockfile places all four affected packages in the development group, while Dependabot assigns mixed scopes.

## Decisions

- Capture a baseline from the committed lockfile in the Python 3.12 project container. Reconcile Dependabot and pip-audit by advisory and affected path, including findings unique to either source.
- Track the initial versions and advisory floors: certifi 2026.5.20 → 2026.10.18, filelock 3.29.0 → 4.2.1, msgpack 1.2.2 → 1.2.3, and urllib3 2.7.0 → 2.8.0. Recheck advisories and compatibility during resolution.
- Prefer compatible parent updates before adding transitive constraints. Verify filelock 4.x against its dependency chain and evaluate compatible upgrades to direct dependencies. Keep the resolution reproducible with Poetry and Python 3.12.
- Compare audits from clean baseline and final installations. Inspect the final production image independently to confirm actual package presence. Record scanner discrepancies and residual findings with paths, impact, mitigation, and evidence.

## Risks / Trade-offs

- The filelock major update may require updating its parent. Confirm resolver and runtime compatibility before accepting the result.
- Advisory data can change during validation. Record findings from the final audit in the same inventory.

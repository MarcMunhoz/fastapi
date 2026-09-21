## Why

The dependency lockfile contains four vulnerable Python packages associated with six open Dependabot alerts, including critical and high-severity advisories in the production dependency graph. Updating the resolved dependencies now removes known vulnerable versions before the template grows code paths that could make the affected behavior reachable.

## What Changes

- Refresh the Poetry lockfile so `anyio`, `starlette`, `pip`, and `msgpack` resolve to versions containing the fixes identified by Dependabot.
- Preserve the existing direct FastAPI and Uvicorn dependency constraints unless dependency resolution proves that a direct constraint must change.
- Verify that production dependencies remain isolated from development-only audit tooling.
- Validate the resolved dependency graph and confirm that all six reported advisories are absent from the updated lockfile.

## Capabilities

### New Capabilities

- `dependency-security`: Defines how production and development Python dependencies are locked, separated, and checked against known vulnerability fixes.

### Modified Capabilities

None.

## Impact

- Affected dependency metadata: `app/poetry.lock`, and `app/pyproject.toml` only if required by the resolver.
- Affected runtime packages: Starlette and AnyIO.
- Affected development packages: pip and msgpack through pip-audit's dependency graph.
- No intended application API or endpoint behavior changes.
- Dependency resolution, auditing, tests, and image builds must run inside the project container.

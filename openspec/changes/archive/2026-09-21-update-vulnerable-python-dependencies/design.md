## Context

See `proposal.md` for motivation. The project declares FastAPI and Uvicorn as direct runtime dependencies and uses pip-audit as development tooling. The packages from the original Dependabot alerts are all transitive dependencies recorded in `app/poetry.lock`: Starlette and AnyIO belong to the main group, while pip and msgpack belong to the development group. The implementation audit additionally identified vulnerable IDNA 3.13 in both groups.

The container build disables Poetry virtual environments and installs main dependencies into the builder image. The production image copies those installed packages, while the development target performs a second install that includes development groups. Dependency commands must run in the container so host-local Poetry environments cannot influence the result.

## Goals / Non-Goals

**Goals:**

- Produce the smallest compatible lockfile refresh that reaches every Dependabot fixed version.
- Preserve the existing separation between runtime and development dependency groups.
- Keep direct dependency constraints unchanged when their current ranges permit a secure resolution.
- Establish evidence that the committed lockfile resolves and audits cleanly in the container environment.

**Non-Goals:**

- Change application routes or API behavior.
- Add new runtime or development tools.
- Upgrade unrelated dependencies solely because newer versions are available.
- Treat a host-local Poetry environment as deployment evidence.

## Decisions

### Use a targeted transitive dependency refresh

Regenerate the lockfile by targeting `anyio`, `starlette`, `pip`, and `msgpack`, then target `idna` after reproducing `PYSEC-2026-215` with the container audit. Their parent constraints admit the fixed versions, so targeted refreshes minimize unrelated churn.

Alternative considered: refresh the entire dependency graph. This could also resolve the alerts but would mix security remediation with unrelated upgrades and increase regression risk.

### Preserve direct constraints unless resolution fails

Keep the FastAPI, Uvicorn, and pip-audit declarations unchanged on the first resolution attempt. If the resolver proves a fixed transitive version is incompatible, update only the direct parent constraint required to make the secure version selectable and document that additional change.

Alternative considered: pin vulnerable transitive packages directly in `pyproject.toml`. This would obscure ownership of those dependencies and create constraints that must be maintained independently from their direct parents.

### Validate both dependency groups inside containers

Validate the main-only production graph separately from the full development graph. The production check establishes that Starlette and AnyIO are remediated without importing audit tooling; the development check establishes that pip, msgpack, and pip-audit remain functional.

Alternative considered: validate only the development environment. That would not prove the production image retains its intended smaller dependency surface.

### Use both lockfile inspection and advisory auditing

Verify the four resolved versions directly in `app/poetry.lock`, then run the project's audit tooling against the resolved graph. Version inspection proves the intended minimums; auditing guards against incorrect assumptions and additional known advisories introduced by resolution.

## Risks / Trade-offs

- [A fixed transitive version is incompatible with a current direct dependency] → Update only the blocking direct dependency and document the resolver evidence.
- [A targeted refresh changes additional transitives] → Review every lockfile delta and retain only resolver-required changes.
- [The advisory database changes between planning and implementation] → Treat newly reported findings as separate evidence and do not claim the six-alert remediation complete until all six original advisory identifiers are absent.
- [Development-only packages accidentally enter production] → Compare Poetry group metadata and validate the production image independently.
- [A container build uses cached dependency layers] → Perform the final dependency validation from the committed lockfile in a clean container build context.

## Migration Plan

1. Resolve the vulnerable transitive packages inside the project container, including any additional package identified by the implementation audit.
2. Review the lockfile delta and confirm the fixed minimum versions and dependency groups.
3. Validate Poetry metadata, dependency auditing, application checks, and both container targets.
4. Push the lockfile change and confirm GitHub closes all six Dependabot alerts.

Rollback consists of reverting the dependency metadata commit and rebuilding the previous container image. Because the change has no data migration or API changes, no application-state rollback is required.

## Validation Evidence

- The targeted container update resolved AnyIO 4.15.1, Starlette 1.6.0, pip 26.2.1, msgpack 1.2.2, IDNA 3.20, and the required typing-extensions 4.16.0 dependency.
- `poetry check` completed successfully inside the development container, with only pre-existing deprecation warnings for legacy Poetry metadata fields.
- The first `pip-audit` run proved `PYSEC-2026-215` was present through IDNA 3.13; after the targeted IDNA update, the audit reported no known vulnerabilities.
- The clean audit covers the original advisories CVE-2026-63374, CVE-2026-64847, CVE-2026-13346, GHSA-6v7p-g79w-8964, CVE-2026-54283, and CVE-2026-54282, plus `PYSEC-2026-215`.
- Container-local HTTP checks returned `{'message': 'Hello, World!'}` from `/` and `{'status': 'ok'}` from `/health`.
- Both development and production targets built successfully from the updated lockfile.
- The production image reported AnyIO 4.15.1, Starlette 1.6.0, and IDNA 3.20, while `pip-audit`, msgpack, pytest, and Ruff were absent.

## Context

See `proposal.md` for motivation. The project declares FastAPI and Uvicorn as direct runtime dependencies and uses pip-audit as development tooling. The vulnerable packages are all transitive dependencies recorded in `app/poetry.lock`: Starlette and AnyIO belong to the main group, while pip and msgpack belong to the development group.

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

Regenerate the lockfile by targeting `anyio`, `starlette`, `pip`, and `msgpack`. Their parent constraints already admit the fixed versions identified by Dependabot, so a targeted refresh minimizes unrelated churn.

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

1. Resolve only the four vulnerable transitive packages inside the project container.
2. Review the lockfile delta and confirm the fixed minimum versions and dependency groups.
3. Validate Poetry metadata, dependency auditing, application checks, and both container targets.
4. Push the lockfile change and confirm GitHub closes all six Dependabot alerts.

Rollback consists of reverting the dependency metadata commit and rebuilding the previous container image. Because the change has no data migration or API changes, no application-state rollback is required.

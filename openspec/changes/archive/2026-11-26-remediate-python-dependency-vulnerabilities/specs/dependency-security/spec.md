## ADDED Requirements

### Requirement: Dependency maintenance accounts for advisory findings

The project SHALL reconcile repository alerts and containerized Python audit results against the committed dependency graph.

#### Scenario: Establish the advisory baseline
- **WHEN** the maintenance round inventories the committed lockfile
- **THEN** it records advisory IDs, affected paths, actual dependency groups, installed versions, available patched versions, and discrepancies between scanners

#### Scenario: Compare the final installed graph
- **WHEN** the updated lockfile is installed and audited in a clean container
- **THEN** the inventory records the disposition of every baseline and newly discovered finding, with evidence and mitigation for any remaining exposure

### Requirement: Dependency updates preserve runtime compatibility

The project SHALL verify the updated lockfile on Python 3.12 and confirm the development and production dependency boundaries.

#### Scenario: Validate compatible updates in containers
- **WHEN** the affected chains and compatible direct updates are resolved
- **THEN** the lockfile records the remediated versions, Ruff and pytest pass, and the production build serves successful responses at `/` and `/health`

#### Scenario: Confirm actual production exposure
- **WHEN** the final production image is inspected
- **THEN** its installed package inventory confirms whether each affected package is present and development-only audit tooling remains excluded

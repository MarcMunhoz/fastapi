# Dependency Security Specification

## Purpose

Defines the security and reproducibility guarantees for Python dependencies used by the production application and its development tooling.

## Requirements

### Requirement: Locked dependencies exclude reported vulnerable versions
The project SHALL lock Python dependencies to versions that are outside the vulnerable ranges reported by the six open Dependabot alerts addressed by this change.

#### Scenario: Production dependency fixes are locked
- **WHEN** the production dependency graph is resolved
- **THEN** `anyio` SHALL resolve to version 4.14.2 or newer
- **AND** `starlette` SHALL resolve to version 1.3.1 or newer
- **AND** `idna` SHALL resolve to version 3.15 or newer

#### Scenario: Development dependency fixes are locked
- **WHEN** the development dependency graph is resolved
- **THEN** `pip` SHALL resolve to version 26.2.0 or newer
- **AND** `msgpack` SHALL resolve to version 1.2.1 or newer

### Requirement: Dependency groups remain isolated
The project MUST keep audit and test tooling outside the production dependency installation.

#### Scenario: Production dependencies are installed
- **WHEN** the production image installs only the main dependency group
- **THEN** development-only packages introduced through `pip-audit` SHALL NOT be installed

#### Scenario: Development dependencies are installed
- **WHEN** the development image installs all configured dependency groups
- **THEN** security audit tooling SHALL remain available

### Requirement: Dependency remediation is reproducible
The project SHALL record the remediated dependency graph in the version-controlled Poetry lockfile and validate it inside the project container.

#### Scenario: A clean environment installs dependencies
- **WHEN** dependencies are installed from the committed project metadata and lockfile
- **THEN** the resolver SHALL select the recorded remediated versions without requiring host-local dependency state

#### Scenario: The remediated graph is audited
- **WHEN** the committed dependency graph is checked against the advisory database
- **THEN** none of the six Dependabot advisories addressed by this change SHALL be reported
- **AND** the additional `PYSEC-2026-215` advisory discovered during implementation SHALL NOT be reported

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

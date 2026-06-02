# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 2026-06-02

### [v0.0.6]

#### Added
- `start-dev` Makefile target to start an existing Docker Compose service.
- `audit` Makefile target to run dependency vulnerability checks inside the container.

#### Changed
- Version bumped to `0.0.6` in project metadata and Docker image labels.
- Docker image documentation updated to reference the `0.0.6` tag.
- `up-dev` now rebuilds, recreates, and removes orphaned Docker Compose services.
- `logs` now prints current Docker Compose logs without following the stream.
- Locked dependencies updated, including idna and starlette security fixes.

## 2026-05-11

### [v0.0.5]

#### Added
- Ruff configuration for linting and formatting.
- Pytest configuration and coverage tooling dependencies.
- Git ignore rules for local coverage and pytest artifacts.

#### Changed
- Version bumped to `0.0.5` in project metadata and Docker image labels.
- Docker image documentation updated to reference the `0.0.5` tag.

### [v0.0.4]

#### Added
- Health check endpoint (`GET /health`) returning the application status.

#### Changed
- Version bumped to `0.0.4` in project metadata and Docker image labels.
- Docker image documentation updated to reference the `0.0.4` tag.
- README usage commands aligned with the current Makefile targets.

## [v0.0.2] - 2025-06-27

### Added
- `pyproject.toml` and `poetry.lock` for dependency management via Poetry.
- `tests/` directory placeholder for future unit tests.

### Changed
- Project structure moved to `/app` folder for clearer separation of source code and infrastructure.
- Dockerfile updated to install and use Poetry instead of requirements.txt.
- Docker now runs `poetry run uvicorn` as the default command.
- Version bumped to `0.0.2` in `pyproject.toml`.

### Removed
- `requirements.txt` is no longer needed due to Poetry.

## [v0.0.1] - 2025-06-23

### Added
- Initial project setup with FastAPI and Docker.
- Basic API endpoint (`GET /`) returning "Hello, World!".
- Dockerfile using Python 3.13.5-alpine.
- docker-compose.yaml for easy development setup.
- Swagger UI and ReDoc enabled automatically.
- Added README.md and CHANGELOG.md files.

## [Unreleased]

### Added
- Planned: Deployment instructions for cloud platforms (e.g., Render, Railway, AWS).
- Planned: Example with database (PostgreSQL or SQLite).

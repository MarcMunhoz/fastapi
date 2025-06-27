# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

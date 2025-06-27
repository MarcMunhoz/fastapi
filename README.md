# FastAPI Docker Template

This is a simple and lightweight template for building a FastAPI application using Python 3.12 (Alpine-based) with Docker and Docker Compose.

## 🚀 Features

- FastAPI (ASGI framework)
- Poetry for dependency and project management
- Dockerized with Python 3.12 (Alpine-based)
- Hot-reload for development with Uvicorn
- Auto-generated Swagger UI and ReDoc documentation
- Clean project structure with isolated source code and tests

## 🗂️ Project Structure

```
.
├── app/
│   ├── main.py
│   ├── pyproject.toml
│   ├── poetry.lock
│   └── tests/
│       └── __init__.py
├── Dockerfile
├── docker-compose.yaml
├── Makefile
├── README.md
├── CHANGELOG.md
├── LICENSE
└── .dockerignore
```

## 🐳 Running the Application with Docker

### Build and start the container

```bash
make up
```

This will install dependencies using Poetry and run the app via Uvicorn with auto-reload.

### Access the API

- API Root: [http://localhost:8000](http://localhost:8000)
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Stop the container

```bash
make stop
```

### Remove container and image

```bash
make down
```

## 🧠 API Example

```bash
curl http://localhost:8000/
```

Response:

```json
{"message": "Hello, World!"}
```

## 🧪 Running Tests

> Test scaffolding is located under `app/tests/`. Add your unit tests there.

## ⚙️ Development

Open a shell inside the running container:

```bash
make shell
```

## 📦 Dependency Management

Dependencies are managed using [Poetry](https://python-poetry.org/). To add a new package:

```bash
poetry add <package-name>
```

## 🏷️ Versioning

This project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html). All notable changes are documented in the [CHANGELOG](CHANGELOG.md).

## ⚖️ License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
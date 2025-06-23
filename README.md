# FastAPI Docker Template

This is a simple and lightweight template for building a FastAPI application using Python 3.13.5 with Docker and Docker Compose.

## 🚀 Features

- FastAPI (ASGI framework)
- Dockerized with Python 3.13.5 (Alpine-based)
- Hot-reload for development
- OpenAPI & Swagger UI documentation
- Easy deployment using Docker Compose

## 🗂️ Project Structure

```
.
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
├── main.py
├── README.md
├── CHANGELOG.md
└── .dockerignore
```

## 🐳 Running the Application with Docker

### Build and start the container

```bash
make up
```

### Access the API

- API Root: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Stop the container

```bash
make stop
```

### Remove container and Image

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

## 📦 Requirements

Check `requirements.txt` for Python dependencies.

## 🔧 Development

Access the container shell if needed:

```bash
make shell
```

## ⚖️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

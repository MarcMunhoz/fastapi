# FastAPI Boilerplate Docker Image

A lightweight Docker image for running FastAPI applications with Uvicorn.

This image is published from the GitHub repository workflow and is intended as a minimal starter image for FastAPI APIs using Python 3.12 on Alpine Linux.

## 🚀 Features

- ✅ Python 3.12 Alpine-based image
- ✅ FastAPI with Uvicorn
- ✅ Swagger UI and ReDoc enabled by default
- ✅ Development and production Docker stages
- ✅ Poetry-based dependency management

## 🐳 Usage

Pull a specific version:

```bash
docker pull himunhoz/fastapi_img:0.0.3
```

Run the container:

```bash
docker run -p 8000:8000 himunhoz/fastapi_img:0.0.3
```

Then open:

```text
http://localhost:8000
```

API documentation:

- Swagger UI: `/docs`
- ReDoc: `/redoc`

## 🏷️ Tags

- `latest`: latest published image from the stable branch workflow
- `0.0.3`: current semantic version
- `sha-...`: commit-specific image tag for traceability

Prefer versioned tags such as `0.0.3` for reproducible deployments. Use `latest` only when you intentionally want the newest published image.

## 🏗️ As a Base Image

```Dockerfile
FROM himunhoz/fastapi_img:0.0.3

COPY ./app /app
```

## 🔗 Source

The source code and release history are available in the GitHub repository for this project.

## 📄 License

This project is licensed under the MIT License.

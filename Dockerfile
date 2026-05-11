FROM python:3.12-alpine AS base

LABEL author="Marcelo Munhoz <me@marcelomunhoz.com>" \
  description="FastAPI boilerplate with Docker" \
  version="0.0.5" \
  date_created="2026-05-07"

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  POETRY_VERSION=2.1.3 \
  PATH="/root/.local/bin:$PATH"

WORKDIR /app

FROM base AS builder

RUN apk add --no-cache build-base curl && \
  curl -sSL https://install.python-poetry.org | python3 - --version $POETRY_VERSION

COPY app/pyproject.toml app/poetry.lock ./

RUN poetry config virtualenvs.create false && \
  poetry install --only main --no-root

FROM builder AS dev

COPY app/ .

RUN poetry install --no-root

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM base AS prod

RUN apk add --no-cache libstdc++

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY app/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

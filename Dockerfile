FROM python:3.12-alpine

LABEL author="Marcelo Munhoz <me@marcelomunhoz.com>" \
  description="FastAPI boilerplate with Docker" \
  version="0.1.0" \
  date_created="2025-06-25"

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=2.1.3
ENV PATH="/root/.local/bin:$PATH"

# Instala o curl e poetry
RUN apk add --no-cache build-base curl
RUN curl -sSL https://install.python-poetry.org | python3 - --version $POETRY_VERSION

WORKDIR /app

COPY app/ .

# Instala dependências sem virtualenv
RUN poetry config virtualenvs.create false && \
    poetry install --no-root && \
    rm -rf /var/cache/apk/* /tmp/* /var/tmp/* /usr/share/man

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
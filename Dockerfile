FROM python:3.13.5-alpine

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Instalar dependências de sistema
RUN apk update && apk add --no-cache \
    build-base \
    libffi-dev \
    musl-dev \
    gcc \
    postgresql-dev \
    && pip install --upgrade pip

# Diretório de trabalho
WORKDIR /app

# Copiar dependências
COPY requirements.txt .

# Instalar dependências Python
RUN pip install -r requirements.txt

# Copiar código-fonte
COPY . .

# Expõe a porta
EXPOSE 8000

# Comando para executar
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
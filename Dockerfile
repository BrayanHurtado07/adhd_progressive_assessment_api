FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# dependencias mínimas para asyncpg
RUN apt-get update && apt-get install -y gcc build-essential musl-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copia código y artefactos (el modelo)
COPY app ./app
COPY artifacts ./artifacts

# puerto de la app
EXPOSE 8000

# gunicorn con worker uvicorn (asíncrono)
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "2", "-b", "0.0.0.0:8000", "app.main:app"]

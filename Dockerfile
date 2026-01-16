# syntax=docker/dockerfile:1

# Stage: builder (instalacja zależności)
FROM python:3.12-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

# system deps for building some python packages if needed
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --prefix=/install --no-cache-dir -r requirements.txt

# Stage: runtime (mniejszy obraz)
FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

# skopiuj zainstalowane pakiety
COPY --from=builder /install /usr/local

# skopiuj kod aplikacji
COPY app ./app

# katalog na dane sqlite (wolumen) i nadaj własność całego /app
RUN adduser --disabled-password --gecos "" appuser || true \
    && mkdir -p /app/data \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# domyślna zmienna (można nadpisać w docker-compose)
ENV DATABASE_URL=sqlite:///./data/dev.db

# uruchomienie uvicorn jako moduł (bez reload w obrazie produkcyjnym)
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


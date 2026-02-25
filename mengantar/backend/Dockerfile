# Stage 1: Build
FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir --prefix=/install .

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /install /usr/local
COPY . .

# Create data directory and non-root user
RUN mkdir -p data && \
    useradd -m chatbot && \
    chown -R chatbot:chatbot /app

USER chatbot

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

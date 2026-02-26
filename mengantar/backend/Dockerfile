# Stage 1: Build
FROM python:3.12 AS builder

WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
# Alternatively, if ghcr is unreachable at all, we can fallback to:
# RUN pip install uv

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Copy only the files needed for installation to improve caching
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-install-project --no-dev

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (curl for healthcheck, postgresql-client for pg_isready)
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the project files
COPY . .

# Install dependencies directly using uv
RUN uv sync --frozen --no-dev

# Ensure we use the virtualenv
ENV PATH="/app/.venv/bin:$PATH"

# Create data directory and non-root user
RUN mkdir -p data && \
    useradd -m chatbot && \
    chmod +x entrypoint.sh && \
    chown -R chatbot:chatbot /app

USER chatbot

EXPOSE 8000

CMD ["./entrypoint.sh"]

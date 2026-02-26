#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h postgres -p 5432 -U postgres; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - executing migrations"

# Run Alembic migrations
# Use 'uv run' to ensure we use the virtual environment
uv run alembic upgrade head

echo "Migrations completed - building FAISS index"

uv run python -m app.rag.knowledge_base

echo "FAISS index built - starting backend server"

# Start the FastAPI application with multiple workers
exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

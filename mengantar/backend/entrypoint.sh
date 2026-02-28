#!/bin/bash
set -e

# Extract host and port from DATABASE_URL if it exists
# Format: postgresql://user:pass@host:port/dbname
if [[ -n "$DATABASE_URL" ]]; then
  # Use sed to extract the host part (everything after @ and before : or /)
  DB_HOST=$(echo "$DATABASE_URL" | sed -e 's|.*@\(.*\):.*|\1|' -e 's|.*@\(.*\)/.*|\1|')
  DB_PORT=$(echo "$DATABASE_URL" | sed -e 's|.*:\([0-9]*\)/.*|\1|' | grep -E '^[0-9]+$' || echo "5432")
else
  DB_HOST="postgres"
  DB_PORT="5432"
fi

echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."
until pg_isready -h "$DB_HOST" -p "$DB_PORT"; do
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

# Start the FastAPI application with auto-reload for development
# For production, use --workers 4 instead
exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

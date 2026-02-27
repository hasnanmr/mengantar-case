# Deployment Guide

This document provides instructions on how to deploy the backend and frontend of the AI Sales Chatbot.

## Docker Deployment (Recommended)

The easiest way to run the entire system is using Docker Compose.

1. **Configuration**: Ensure `.env` files are set up in `backend/`.
2. **Start Services**:
   ```bash
   docker-compose up --build
   ```
   > [!NOTE]
   > On startup, the backend container will automatically:
   > 1. Wait for PostgreSQL to be ready.
   > 2. Run database migrations (`alembic upgrade head`).
   > 3. **Build the FAISS knowledge index** (`app.rag.knowledge_base`).

3. **Access**:
   - Backend API: `http://localhost:8000`
   - Frontend: `http://localhost:3000`

## Local Development Setup

### Backend

1. Navigate to `backend/`.
2. Install dependencies: `uv sync`.
3. **Database Setup**: You can run PostgreSQL via Docker but access it locally:
   - Run `docker-compose up -d postgres` (ensure port `5432` is exposed in `docker-compose.yaml`).
   - The default `DATABASE_URL` in `.env` is `postgresql://postgres:postgres@localhost:5432/postgres`.
4. **Run Server**: Use the provided `Makefile` for convenience:
   ```bash
   make api-dev
   ```
   Alternatively, run manually: `uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`.

### Frontend

1. Navigate to `frontend/`.
2. Install dependencies: `npm install` or `pnpm install`.
3. Start development server: `npm run dev`.

## Troubleshooting

### PostgreSQL Connection

If you see connection errors, ensure the `DATABASE_URL` in your `.env` matches your PostgreSQL configuration. If running Postgres in Docker, ensure the container is running: `docker ps`. If it stopped, run `docker start mengantar-postgres`.

### OMP: Error #15 (macOS)

If the backend crashes with `OMP: Error #15: Initializing libomp.dylib...`, this is due to multiple OpenMP runtimes being loaded. The fix is already implemented in `app/main.py` via `os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"`.

### Langfuse v3 Migration

The system uses **Langfuse v3**.
- Credentials are read from `.env` and passed via `app/core/config.py`.
- **Session IDs** and **Tags** are passed via `config["metadata"]` in LangChain/LangGraph invocations, not via the context manager as in v2.
- Ensure the `CallbackHandler` from `langfuse.langchain` is used.

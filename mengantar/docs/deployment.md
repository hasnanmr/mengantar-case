# Deployment Guide

This document provides instructions on how to deploy the backend and frontend of the AI Sales Chatbot.

## API Documentation

For detailed information about the backend API endpoints used by the frontend, see:
- [Backend to Frontend API Documentation](./API.md)

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

### Testimonial Data Seeding

To populate the testimonial database and FAISS index:
1. Ensure the image files are present in `backend/static/testimonials/` (e.g., `amanda.jpg`, `silmi.jpg`).
2. Run the seeding script:
   ```bash
   cd backend
   uv run python -m scripts.seed_testimonials
   ```
   This will:
   - Clear existing testimonials in PostgreSQL.
   - Insert new records with the correct image paths.
   - Rebuild the `data/faiss_index/testimonials` vector store.

---

## Langfuse v3 Migration
...

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
   > On startup, the backend container will automatically wait for PostgreSQL to be ready and run the necessary database migrations (`alembic upgrade head`).

3. **Access**:
   - Backend API: `http://localhost:8000`
   - Frontend: `http://localhost:3000`

## Local Development Setup

### Backend

1. Navigate to `backend/`.
2. Install `uv` if not already installed: `curl -LsSf https://astral.sh/uv/install.sh | sh`.
3. Install dependencies: `uv sync`.
4. **Database Migration**: Ensure PostgreSQL 17 is running locally, then run the migrations:
   ```bash
   export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres
   uv run alembic upgrade head
   ```
5. Run the server: `uv run uvicorn app.main:app --reload`.

### Frontend

1. Navigate to `frontend/`.
2. Install dependencies: `npm install`.
3. Start development server: `npm run dev`.

## Troubleshooting

### PostgreSQL Connection

If you see connection errors, ensure the `DATABASE_URL` in your `.env` matches your PostgreSQL configuration and that the database is accessible.

### ModuleNotFoundError: langfuse.callback

The system has been upgraded to Langfuse v3. If you encounter a `ModuleNotFoundError` for `langfuse.callback`, ensure the code is using the new import: `from langfuse.langchain import CallbackHandler`.

### Python 3.12 Requirement

The backend now requires Python 3.12. If running locally, ensure your environment is updated (`uv python install 3.12`).

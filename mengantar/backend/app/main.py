"""
FastAPI main application entry point.
"""
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.threads import router as threads_router
from fastapi.staticfiles import StaticFiles

from app.core.db import init_pool, close_pool, get_pool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """App lifespan events."""
    logger.info("🚀 Acne Care Sales Chatbot Backend starting up...")
    await init_pool()
    
    # Initialize LangGraph's own tables idempotently (no-op if tables already exist).
    # This ensures list_threads and other checkpoints-dependent logic won't fail.
    async with get_pool().connection() as conn:
        checkpointer = AsyncPostgresSaver(conn)
        await checkpointer.setup()
        logger.info("LangGraph PostgreSQL checkpointer tables initialized.")
        
    yield
    await close_pool()
    logger.info("👋 Acne Care Sales Chatbot Backend shutting down...")


app = FastAPI(
    title="Acne Care Sales Chatbot API",
    description="AI-powered sales chatbot for Acne Care Cream using LangGraph + Qwen on OpenRouter.",
    version="1.0.0",
    lifespan=lifespan,
    # redirect_slashes=True by default
)

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://frontend:3000",
        "https://hasnan.cloud",
        "https://www.hasnan.cloud"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(chat_router, prefix="/api")
app.include_router(threads_router, prefix="/api")

# Serve static files from the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return {"status": "ok", "message": "Acne Care Chatbot API is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}

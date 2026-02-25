"""
FastAPI main application entry point.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.threads import router as threads_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """App lifespan events."""
    logger.info("🚀 Acne Care Sales Chatbot Backend starting up...")
    yield
    logger.info("👋 Acne Care Sales Chatbot Backend shutting down...")


app = FastAPI(
    title="Acne Care Sales Chatbot API",
    description="AI-powered sales chatbot for Acne Care Cream using LangGraph + Qwen on OpenRouter.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api")
app.include_router(threads_router, prefix="/api")


@app.get("/")
async def root():
    return {"status": "ok", "message": "Acne Care Chatbot API is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}

# Acne Care Chatbot — Backend

AI-powered sales chatbot backend built with **Python**, **FastAPI**, and **LangGraph**.

## Stack
- **LangGraph** (2 agents: `customer_service`, `marketing_promotion`)
- **FastAPI** + Uvicorn with SSE streaming
- **OpenRouter** (LLM: `Qwen3-32b`)
- **Qwen3-Embedding-8B** for RAG
- **FAISS** for vector store
- **SQLite** for thread memory (LangGraph checkpointer)

## Setup

1. Copy `.env.example` to `.env` and fill in your OpenRouter API key:
   ```
   cp .env.example .env
   ```

2. Install:
   ```
   pip install -e .
   ```

3. Build FAISS index:
   ```
   make build-index
   ```

4. Run:
   ```
   make api-dev
   ```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/` | Send chat message (SSE) |
| GET | `/api/threads/` | List all threads |
| GET | `/api/threads/{thread_id}` | Get thread detail |
| DELETE | `/api/threads/{thread_id}` | Delete thread |

## SSE Event Format

```json
{"type": "token", "content": "..."}
{"type": "usage", "input_tokens": 120, "output_tokens": 80, "total_tokens": 200}
{"type": "done", "thread_id": "...", "stage": "consultation"}
{"type": "error", "content": "..."}
```

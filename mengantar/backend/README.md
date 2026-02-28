# Acne Care Chatbot — Backend

AI-powered sales chatbot backend built with **Python**, **FastAPI**, and **LangGraph**.

## Live Demo
- **Frontend**: https://hasnan.cloud
- **Backend API**: https://api.hasnan.cloud

## Stack
- **LangGraph v1.0.3** (multi-agent orchestration)
- **FastAPI v0.121.2** + Uvicorn with SSE streaming
- **OpenRouter** (LLM: `qwen/qwen3.5-35b-a3b`)
- **Qwen3-Embedding-4B** (`qwen/qwen3-embedding-4b`) for RAG embeddings
- **FAISS** for vector store
- **PostgreSQL 17** for thread memory (LangGraph checkpointer)
- **Langfuse v3.11.1** for observability and tracing

## Agents

### 1. Customer Service Agent (`customer_service`)
- **Persona**: Sari - Customer Service Skincare Consultant
- **Stages**: `greeting` → `needs_assessment` → `consultation`
- **Fungsi**:
  - Menyapa pelanggan dan memahami kebutuhan kulit mereka
  - Konsultasi produk ACSBP (Acne Cleanser Scrub Beta Plus)
  - Menjawab pertanyaan seputar kandungan, manfaat, dan cara pakai
  - Handoff ke Marketing jika user minta foto/testimoni visual atau tanya promo

### 2. Marketing Promotion Agent (`marketing_promotion`)
- **Persona**: Dinda - Digital Marketing Specialist
- **Stages**: `social_proof` → `promotion` → `closing`
- **Fungsi**:
  - Menampilkan testimoni visual (foto) dari pengguna produk
  - Menawarkan promo dan diskon (Beli 2 Gratis 1)
  - Closing penjualan dan mengarahkan ke pembelian
  - Handoff kembali ke Customer Service jika user butuh konsultasi lanjutan

## Setup

1. Copy `.env.example` to `.env` and fill in your OpenRouter API key and Langfuse credentials:
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

## Token Counting

Token dihitung **per turn** (setiap request/response cycle):

| Komponen | Penjelasan |
|----------|------------|
| **Tokenizer** | Qwen2.5-7B-Instruct (proxy untuk Qwen3) |
| **Input Tokens** | System prompt + user message |
| **Output Tokens** | AI response |
| **Storage** | Disimpan di `state.token_log` per thread |
| **SSE Event** | Mengirim token usage terakhir via `usage` event |
| **Frontend** | Ditampilkan sebagai badge di bawah setiap response: `🔢 in:X out:Y total:Z` |

Fallback ke estimasi karakter (1 token ≈ 4 karakter) jika tokenizer gagal load.

# AI Sales Chatbot - Recruitment Usecase

This project is an AI-powered sales chatbot designed for recruitment use cases. It leverages LangGraph for complex agentic workflows, FAISS for efficient document retrieval (RAG), PostgreSQL 17 for persistent storage and thread checkpointing, and a modern frontend for user interaction.


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

## Quick Start
- **Frontend**: https://hasnan.cloud
- **Backend API**: https://api.hasnan.cloud
- **Backend docs API**: https://api.hasnan.cloud/docs
- **Billing token API-Key dari openrouter untuk development selama 3 hari untuk mencoba testing hanya mencapai $0.2**

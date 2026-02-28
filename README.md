# AI Sales Chatbot - Recruitment Usecase

This project is an AI-powered sales chatbot designed for recruitment use cases. It leverages LangGraph for complex agentic workflows, FAISS for efficient document retrieval (RAG), PostgreSQL 17 for persistent storage and thread checkpointing, and a modern frontend for user interaction.

## Project Structure

- `backend/`: Fast API backend implementation.
- `frontend/`: React-based frontend application.
- `docs/`: Comprehensive technical documentation.

## Documentation Index

Detailed documentation can be found in the [`docs/`](./docs/) directory:

1. [LangGraph Architecture](./docs/architecture.md)
2. [Frontend Overview](./docs/frontend.md)
3. [FAISS Retrieval System](./docs/retrieval.md)
4. [Chunking Strategy](./docs/chunking.md)
5. [Persistence & Thread Checkpoints](./docs/persistence.md)
6. [Model Routing](./docs/routing.md)
7. [Deployment Guide](./docs/deployment.md)
8. [Testing Guide](./docs/testing.md)
9. [PostgreSQL Setup Guide](./docs/postgres_setup.md)
10. [Database Migration Guide](./docs/database_migrations.md)

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
## Quick Start

Refer to the [Deployment Guide](./docs/deployment.md) for instructions on how to set up and run the project.
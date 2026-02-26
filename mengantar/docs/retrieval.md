# FAISS Retrieval System

This document explains how the retrieval mechanism works using FAISS (Facebook AI Similarity Search) and how it integrates with the LangGraph state machine to generate an LLM response.

## Architecture Flow

The following sequence diagram illustrates the entire flow from a user message to the final streamed LLM response, including the retrieval step:

```mermaid
sequenceDiagram
    participant User
    participant API as Chat API (/chat)
    participant Graph as LangGraph Router
    participant Agent as Customer Service Agent
    participant RAG as Knowledge Base (FAISS)
    participant LLM as OpenRouter (LLM)

    User->>API: POST /chat {message, thread_id}
    API->>Graph: Initialize ChatState and Stream
    Graph->>Graph: Determine Stage (greeting, needs_assessment, consultation)
    Graph->>Agent: Route to customer_service_node

    rect rgb(240, 248, 255)
        Note over Agent,RAG: 1. Retrieval Phase
        Agent->>RAG: query_knowledge(Last User Message)
        alt FAISS index exists
            RAG-->>Agent: Relevant Markdown Chunks
        else FAISS index missing
            RAG-->>Agent: Empty Context (WARNING: FAISS index not found)
        end
    end

    rect rgb(255, 250, 240)
        Note over Agent,LLM: 2. Generation Phase
        Agent->>Agent: Construct System Prompt with Retrieved Context
        Agent->>LLM: invoke([SystemMessage, History, HumanMessage])
        
        loop Stream Output
            LLM-->>Agent: Token Stream chunk
            Agent-->>Graph: Yield Token
            Graph-->>API: Yield Token Event (SSE)
            API-->>User: data: {"type": "token", "content": "..."}
        end
    end

    Agent-->>Graph: Update ChatState (Next Stage, Token Logs)
    Graph-->>API: Return Final State
    API-->>User: data: {"type": "done", "stage": "..."}
```

## How it Works

1. **Embedding**: Product knowledge (`product_knowledge.py`) is converted into vector chunks using an embedding model (e.g., `Qwen/Qwen2.5-1.5B-Instruct` or equivalent HuggingFace model).
2. **Indexing**: These vectors are stored in a FAISS index (`vdb/index.faiss`) for fast similarity search.
3. **Querying (Retrieval)**: When a user asks a question, the query is embedded, and the most similar vectors are retrieved from the index via `query_knowledge()`. If the index file is missing, it returns an empty context string.
4. **LLM Generation**: The retrieved text chunks are injected into the context variable of the `CUSTOMER_SERVICE_SYSTEM_PROMPT`. The LLM generates a response based on this context.

## Troubleshooting

### `WARNING - FAISS index not found. Returning empty context.`
This warning occurs because the backend is trying to retrieve context for the user's message, but the local FAISS index files have not been generated yet. 

**Solution**:
You need to generate the FAISS index by running the `build_faiss_index()` function inside `backend/app/rag/knowledge_base.py`.
You can do this by running the file directly inside the backend container:

```bash
uv run python -m app.rag.knowledge_base
```
Once generated, the files (`index.faiss` and `chunks.pkl`) will be created in the local directory (typically mapped to `vdb/` or `.faiss/`), and the system will successfully retrieve the knowledge chunks on the next chat interaction.

# LangGraph Architecture

This document describes the agentic workflow of the AI Sales Chatbot implemented using LangGraph.

## Overview

The backend uses LangGraph to manage the conversation flow as a state machine. This allows for complex logic, error handling, and multi-step reasoning.

## Graph Design

- **Architecture**: A Router Node acts as the entry point, directing the conversation to the appropriate agent node based on the user's current stage. It supports **multi-node execution** within a single turn, allowing for seamless agent handoffs (e.g., from Customer Service to Marketing) without extra user input.
- **Nodes**: specialized agents (`customer_service`, `marketing_promotion`) that process the user's input.
- **State**: The `ChatState` object tracks conversation history, user needs, RAG context, and **token usage logs**.
- **Persistence**: **PostgreSQL** serves as the persistent backend for conversation checkpoints via `AsyncPostgresSaver`, allowing the router to remember the conversation stage across turns.

## Key Components

- **Customer Service Node (Sari)**: Handles greeting (with product intro), needs assessment, and RAG-powered consultation.
  - **Handoff Logic**: If a user asks for photos or testimonials, Sari triggers a `[HANDOFF_TO_MARKETING]` signal, which the graph uses to immediately transition to the Marketing node in the same turn.
  - If a user **explicitly declines** to buy or try the product, the agent closes with: *"Terima kasih sudah menghubungi kami, kami siap untuk membantumu lain kali untuk menangani jerawatmu. Semoga jerawatmu semakin membaik 🌟"* followed by a `[USER_REFUSED]` tag.
- **Marketing Promotion Node (Dinda)**: Handles social proof and conversion.
  - **Stage social_proof**: Focuses on displaying testimonial images (`amanda.jpg`, `silmi.jpg`) and describing them without early promotion.
  - **Stage promotion**: Offers bundling deals (Beli 2 Gratis 1) and link to Erhastore once interest is confirmed.
- **Checkpointer**: Manages thread memory across restarts via PostgreSQL.
- **Multimodal Vision**: The `marketing_promotion` agent uses Qwen 3.5's multimodal capabilities to "see" testimonial images (before/after photos). Images are base64-encoded and sent as vision context, allowing the agent to describe them naturally.
- **Anti-Hallucination Logic**: The system enforces strict rules to prevent the LLM from hallucinating products outside the provided knowledge base. This is achieved through prompt constraints and code-level context fallbacks that restrict the agent to information about ACSBP.
- **Hybrid Testimonial Retrieval**: Testimonials are retrieved using a hybrid approach:
  - **FAISS**: For semantic similarity search based on the user's query.
  - **PostgreSQL**: For persistent storage of image paths and metadata, ensuring reliability and maintainability.

## Observability

The system uses **Langfuse** and **OpenTelemetry** for tracing and monitoring:
- **Service Naming**: OpenTelemetry resource attributes are configured in `app/core/config.py` to ensure the service is correctly identified (e.g., `acne-care-chatbot`) in Langfuse.
- **Traces**: Every LLM invocation and node execution is traced using the **Langfuse v3** `CallbackHandler`, initialized via `get_langfuse_handler(**kwargs)`.
- **Sessions & Metadata**: Tracking is handled by passing `session_id` and `tags` to the handler or via `config["metadata"]` with `langfuse_session_id` to group and categorize traces in the Langfuse dashboard.
- **Multimodal Integration**: The `marketing_promotion` node dynamically injects base64-encoded image data into the message history during the `social_proof` stage, allowing the LLM to provide natural commentary on testimonials.
- **Token Usage**: Tracked per node and per session to monitor costs.

## API Communication

The backend exposes REST and SSE endpoints for frontend communication:

| Component | Endpoint | Description |
|-----------|----------|-------------|
| Chat | `POST /api/chat` | SSE stream for real-time chat responses |
| Threads | `GET /api/threads/` | List all conversation threads |
| Thread History | `GET /api/threads/{id}` | Get message history for a thread |
| Delete Thread | `DELETE /api/threads/{id}` | Delete a conversation thread |

See the [API Documentation](./API.md) for detailed request/response formats and event types.

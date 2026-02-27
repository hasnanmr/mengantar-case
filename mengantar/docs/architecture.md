# LangGraph Architecture

This document describes the agentic workflow of the AI Sales Chatbot implemented using LangGraph.

## Overview

The backend uses LangGraph to manage the conversation flow as a state machine. This allows for complex logic, error handling, and multi-step reasoning.

## Graph Design

- **Architecture**: A Router Node acts as the entry point, directing the conversation to the appropriate agent node based on the user's current stage. It gracefully handles re-entry by routing users from the `"end"` stage back to the customer service node for follow-up questions.
- **Nodes**: specialized agents (`customer_service`, `marketing_promotion`) that process the user's input and generate a single response per turn. Each agent node transitions directly to `END` after execution.
- **State**: The `ChatState` object tracks conversation history, user needs, and RAG context.
- **Persistence**: **PostgreSQL** serves as the persistent backend for conversation checkpoints via `AsyncPostgresSaver`, allowing the router to remember the conversation stage across turns.

## Key Components

- **Customer Service Node**: sari, uses RAG to consult on skin needs.
- **Marketing Promotion Node**: dinda, follows up with social proof and promos.
- **Checkpointer**: Manages thread memory across restarts.
- **Multimodal Vision**: The `marketing_promotion` agent uses Qwen 3.5's multimodal capabilities to "see" testimonial images (before/after photos). Images are base64-encoded and sent as vision context, allowing the agent to describe them naturally.

## Observability

The system uses **Langfuse** and **OpenTelemetry** for tracing and monitoring:
- **Service Naming**: OpenTelemetry resource attributes are configured in `app/core/config.py` to ensure the service is correctly identified (e.g., `acne-care-chatbot`) in Langfuse.
- **Traces**: Every LLM invocation and node execution is traced using the **Langfuse v3** `CallbackHandler`.
- **Sessions & Metadata**: In v3, tracking is handled via `config["metadata"]`. We pass `langfuse_session_id` (using the `thread_id`) and `langfuse_tags` to group and categorize traces in the Langfuse dashboard.
- **Multimodal Integration**: The `marketing_promotion` node dynamically injects base64-encoded image data into the message history during the `social_proof` stage, allowing the LLM to provide natural commentary on testimonials.
- **Token Usage**: Tracked per node and per session to monitor costs.

# LangGraph Architecture

This document describes the agentic workflow of the AI Sales Chatbot implemented using LangGraph.

## Overview

The backend uses LangGraph to manage the conversation flow as a state machine. This allows for complex logic, error handling, and multi-step reasoning.

## Graph Design

- **Architecture**: A Router Node acts as the entry point, directing the conversation to the appropriate agent node based on the user's current stage.
- **Nodes**: specialized agents (`customer_service`, `marketing_promotion`) that process the user's input and generate a single response per turn. Each agent node transitions directly to `END` after execution.
- **State**: The `ChatState` object tracks conversation history, user needs, and RAG context.
- **Persistence**: **PostgreSQL** serves as the persistent backend for conversation checkpoints via `AsyncPostgresSaver`, allowing the router to remember the conversation stage across turns.

## Key Components

- **Customer Service Node**: sari, uses RAG to consult on skin needs.
- **Marketing Promotion Node**: dinda, follows up with social proof and promos.
- **Checkpointer**: Manages thread memory across restarts.

## Observability

The system uses **Langfuse** and **OpenTelemetry** for tracing and monitoring:
- **Service Naming**: OpenTelemetry resource attributes are configured in `app/core/config.py` to ensure the service is correctly identified (e.g., `acne-care-chatbot`) in Langfuse.
- **Traces**: Every LLM invocation and node execution is traced using the Langfuse v3 `CallbackHandler`.
- **Sessions**: Traces are grouped by `thread_id` to allow full conversation review.
- **Token Usage**: Tracked per node and per session to monitor costs.

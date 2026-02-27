# Testing Guide

This document outlines the testing strategy and instructions for the Acne Care chatbot backend.

## Overview

The backend is tested using `pytest` and `pytest-asyncio`. Tests are located in the `backend/tests` directory and cover the following core components:

1.  **Nodes (`test_nodes.py`)**: Validates the behavior of the `customer_service_node` and `marketing_promotion_node`. Key node tests:
    -   `test_customer_service_node_greeting` — verifies that a `greeting` stage response transitions to `needs_assessment`.
    -   `test_customer_service_node_needs_assessment` — verifies that `needs_assessment` stage progresses to `consultation`.
    -   `test_customer_service_node_handoff` — verifies that `[HANDOFF_TO_MARKETING]` triggers transition to `social_proof`.
    -   `test_marketing_promotion_node_progression` / `_closing` — verifies marketing stage transitions.
2.  **Flows (`test_flows.py`)**: Tests the `route_by_stage` routing logic and verifies the LangGraph `StateGraph` structure compiles correctly. Valid customer service stages: `greeting`, `needs_assessment`, `consultation`, `end`.
3.  **Checkpointer (`test_checkpointer.py`)**: Ensures the `AsyncPostgresSaver` initializes correctly and can be attached to the compiled graph.
4.  **Tracing (`test_tracing.py`)**: Verifies that `get_langfuse_handler(**kwargs)` returns a `CallbackHandler` when credentials are set, and `None` when they are missing or empty.

## Running Tests

To run the unit test suite, navigate to the `backend` directory and run:

```bash
cd backend
PYTHONPATH=. uv run pytest tests/ -v
```

> **Note**: `PYTHONPATH=.` is required so that the `app` package is resolvable from the project root when running tests directly.

## Load Testing

A Locust-based load test script is available at `scripts/load_test.py`. It simulates concurrent users sending chat messages to the `/api/chat/` SSE endpoint.

```bash
cd backend
uv run locust -f scripts/load_test.py --host=http://localhost:8000 --headless -u 10 -r 2 -t 30s
```

Parameters:
- `-u` — number of concurrent users
- `-r` — spawn rate (users per second)
- `-t` — total test duration

## Writing Tests

When writing new tests for agent nodes or LangGraph components, keep the following in mind:

-   **Async Support**: Agent nodes are asynchronous — use `@pytest.mark.asyncio` and `await` the node call.
-   **Mocking**: External services (LLMs, Langfuse, database connections) should be mocked using `unittest.mock.patch` to ensure tests run quickly and deterministically without network dependencies.
-   **State**: Check the returned `ChatState` object to verify that `current_stage` and `messages` are updated as expected.
-   **Valid stages**: `ChatState.current_stage` is a `Literal` type. Only use valid stages: `greeting`, `needs_assessment`, `consultation`, `social_proof`, `promotion`, `closing`, `end`.

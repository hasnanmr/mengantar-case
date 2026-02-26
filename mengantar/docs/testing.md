# Testing Guide

This document outlines the testing strategy and instructions for the Acne Care chatbot backend.

## Overview

The backend is tested using `pytest` and `pytest-asyncio`. Tests are located in the `backend/tests` directory and cover the following core components:

1. **Nodes (`test_nodes.py`)**: Validates the behavior of the `customer_service_node` and `marketing_promotion_node`, including state updates and conditional routing parameters.
2. **Flows (`test_flows.py`)**: Tests the `route_by_stage` routing logic and verifies the LangGraph `StateGraph` structure compiles correctly.
3. **Checkpointer (`test_checkpointer.py`)**: Ensures the `AsyncPostgresSaver` initializes correctly and can be attached to the compiled graph.
4. **Tracing (`test_tracing.py`)**: Verifies the initialization of the `LangfuseHandler` based on environment variables.

## Running Tests

To run the unit test suite, navigate to the `backend` directory and run `pytest`:

```bash
cd backend
./.venv/bin/python -m pytest tests/
```

This will discover and run all test files matching the `test_*.py` pattern.

## Writing Tests

When writing new tests for agent nodes or LangGraph components, keep the following in mind:

- **Async Support**: Agent nodes (like `customer_service_node`) are often asynchronous and must be awaited in tests. Use the `@pytest.mark.asyncio` decorator.
- **Mocking**: External services (LLMs, Langfuse, database connections) should be mocked using `unittest.mock.patch` to ensure tests run quickly and deterministically without network dependencies.
- **State**: Check the returned `ChatState` object to verify that `current_stage` and `messages` are updated as expected.

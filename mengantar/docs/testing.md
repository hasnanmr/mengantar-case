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

## Manual Verification

Beyond automated tests, several key features should be verified manually after deployment:

### 1. Testimonial Image Rendering
Ensure that testimonial images (Amanda, Silmi) render correctly in the chat UI.
- **Verification**: Trigger the `social_proof` stage or ask for testimonials. Check that the markdown `![Name](/static/testimonials/...)` is generated and the image is visible.
- **Paths**: Images are served from `static/testimonials/` and mapped via `testimonial_store.py`.

### 2. Anti-Hallucination
Verify that the bot does not recommend products outside the ACSBP knowledge base.
- **Verification**: Ask "Produk ERHA apa lagi yang cocok dipadukan dengan ini?".
- **Expected Result**: The bot should decline to recommend other products or state it only focuses on ACSBP.

### 3. Database-First Testimonials
Confirm that testimonials are being fetched from PostgreSQL.
- **Verification**: Check the backend logs to see if `testimonial_store.search_testimonial` is called successfully. Check the database `mengantar_test.testimonials` table for the correct image paths.

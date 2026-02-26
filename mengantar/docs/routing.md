# Model Routing

This document describes the routing logic used in the Acne Care Sales Chatbot state machine.

## Objective

Routing ensures the conversation flows between specialized agents based on the user's stage and intent.

## Logic Paths

The graph routes between two primary agent nodes:

1. **Customer Service Agent (Sari)**: Handles greetings, needs assessment, and detailed product consultation (RAG).
2. **Digital Marketing Agent (Dinda)**: Handles social proof, promotion, and closing the sale.

## Implementation

Routing is implemented in `app/agents/graph.py` using a **Router Node** architecture:

1. **Router Entry Point**: The graph uses a conditional entry point (`set_conditional_entry_point`) powered by `route_by_stage`. It decides whether the current request should go to the `customer_service` node or the `marketing_promotion` node based on the current stage in the `ChatState`.
2. **Single Response Per Turn**: Once an agent processes the input and generates a response, it updates the `current_stage` if necessary. The node then explicitly transitions to `END`. This ensures only one agent speaks per turn.
3. **Intent-based Handoffs**:
    - `[HANDOFF_TO_MARKETING]`: The CS agent detects if the user asks for "produk baru", "promo", or intent to buy. The CS agent updates the state's `current_stage` to a marketing phase (e.g., `social_proof`), but still routes to `END` for the current turn. On the *next* user input, the router directs traffic to the marketing agent.
    - `[HANDOFF_TO_CUSTOMER_SERVICE]`: Similarly, the Marketing agent can update the stage back to a CS phase (e.g., `consultation`) and route to `END`.

Routing logic can be found in `app/agents/graph.py`.


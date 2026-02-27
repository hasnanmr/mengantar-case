# Model Routing

This document describes the routing logic used in the Acne Care Sales Chatbot state machine.

## Objective

Routing ensures the conversation flows between specialized agents based on the user's stage and intent.

## Logic Paths

The graph routes between two primary agent nodes:

1. **Customer Service Agent (Sari)**: Handles greetings (with product intro), needs assessment, and detailed product consultation (RAG).
2. **Digital Marketing Agent (Dinda)**: Handles social proof, promotion, and closing the sale.

If a user sends a follow-up message after the conversation has reached the `"end"` stage, the router automatically directs them back to the **Customer Service Agent (Sari)**, which will treat the turn as a fresh greeting — including re-introducing the product — before transitioning to `needs_assessment`.

## Conversation Stage Flow

```
greeting → needs_assessment → consultation
                                        ↘
                          social_proof → promotion → closing → end
```

- **`greeting`**: LLM greets the user and introduces the product (Acne Care Cream) in a single natural response. Context provided: Informasi Produk + Bahan Aktif.
- **`needs_assessment`**: LLM asks about the user's skin condition to understand needs.
- **`consultation`**: LLM provides detailed advice using RAG (full product knowledge + testimonials).
- **Marketing stages** (`social_proof`, `promotion`, `closing`): Handled by the Digital Marketing Agent (Dinda).
- **`end`**: Conversation closed. Next user message restarts from `greeting`.

## API Routing Details

The backend API is designed to be flexible with trailing slashes:
- **FastAPI Configuration**: `redirect_slashes=False` is set in `app/main.py`. This ensures that `POST /api/chat` and `POST /api/chat/` are both handled correctly without 307 redirects, which can sometimes interfere with CORS preflight or POST body data.
- **Router Prefixes**: The `/chat` router is included with the `/api` prefix, making the full path `/api/chat/`.

Routing logic can be found in `app/agents/graph.py`.

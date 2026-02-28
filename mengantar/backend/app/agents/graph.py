"""
LangGraph graph definition for the sales chatbot.
Builds the graph with a router node plus customer_service and marketing_promotion nodes.
"""
import logging
from contextlib import asynccontextmanager

import psycopg
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.core.db import get_pool

from app.agents.state import ChatState
from app.agents.customer_service import customer_service_node
from app.agents.marketing_promotion import marketing_promotion_node
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

CUSTOMER_SERVICE_STAGES = ("greeting", "needs_assessment", "consultation")
MARKETING_STAGES = ("social_proof", "promotion", "closing")


def route_by_stage(state: ChatState):
    """Route to the correct agent based on current conversation stage."""
    stage = state.current_stage
    if stage in CUSTOMER_SERVICE_STAGES or stage == "end":
        return "customer_service"
    elif stage in MARKETING_STAGES:
        return "marketing_promotion"
    else:
        return END


def build_graph():
    """Build and compile the LangGraph state machine.
    
    Architecture:
      router → (customer_service | marketing_promotion) → END
    
    Each agent node always routes to END after generating a response, ensuring
    only ONE response is produced per user interaction. The next user message
    will restart at the router, which picks the correct agent based on the
    updated stage stored in the checkpointer.
    """
    builder = StateGraph(ChatState)

    # Add nodes
    builder.add_node("customer_service", customer_service_node)
    builder.add_node("marketing_promotion", marketing_promotion_node)

    # Entry point: router decides which agent handles this turn
    builder.set_conditional_entry_point(
        route_by_stage,
        {
            "customer_service": "customer_service",
            "marketing_promotion": "marketing_promotion",
            END: END,
        }
    )

    def after_customer_service(state: ChatState):
        """Transition to marketing if stage changed, otherwise end turn."""
        if state.current_stage in MARKETING_STAGES:
            return "marketing_promotion"
        return END

    # Add edges
    builder.add_edge("marketing_promotion", END)
    builder.add_conditional_edges(
        "customer_service",
        after_customer_service,
        {
            "marketing_promotion": "marketing_promotion",
            END: END,
        }
    )

    return builder


@asynccontextmanager
async def get_graph_with_checkpointer():
    """Yield the compiled graph with AsyncPostgresSaver checkpointer for thread memory."""
    pool = get_pool()
    async with pool.connection() as conn:
        checkpointer = AsyncPostgresSaver(conn)
        # Initialize LangGraph's own tables idempotently (no-op if tables already exist).
        await checkpointer.setup()

        builder = build_graph()
        graph = builder.compile(checkpointer=checkpointer)
        logger.info("LangGraph compiled with Async PostgreSQL checkpointer.")
        yield graph

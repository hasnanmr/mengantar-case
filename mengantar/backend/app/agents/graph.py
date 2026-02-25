"""
LangGraph graph definition for the sales chatbot.
Builds the graph with customer_service and marketing_promotion nodes.
"""
import os
import logging
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from app.agents.state import ChatState
from app.agents.customer_service import customer_service_node
from app.agents.marketing_promotion import marketing_promotion_node
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def route_by_stage(state: ChatState):
    """Route to the correct agent based on current conversation stage."""
    stage = state.current_stage
    if stage in ("greeting", "needs_assessment", "consultation"):
        return "customer_service"
    elif stage in ("social_proof", "promotion", "closing"):
        return "marketing_promotion"
    else:
        return END


def build_graph():
    """Build and compile the LangGraph state machine."""
    builder = StateGraph(ChatState)

    # Add nodes
    builder.add_node("customer_service", customer_service_node)
    builder.add_node("marketing_promotion", marketing_promotion_node)

    # Entry point
    builder.set_entry_point("customer_service")

    # Conditional routing from customer_service
    builder.add_conditional_edges(
        "customer_service",
        route_by_stage,
        {
            "customer_service": "customer_service",
            "marketing_promotion": "marketing_promotion",
            END: END,
        }
    )

    # Conditional routing from marketing_promotion
    builder.add_conditional_edges(
        "marketing_promotion",
        route_by_stage,
        {
            "marketing_promotion": "marketing_promotion",
            "customer_service": "customer_service",
            END: END,
        }
    )

    return builder


async def get_graph_with_checkpointer():
    """Get the compiled graph with SQLite checkpointer for thread memory."""
    db_path = settings.sqlite_db_path
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    checkpointer = SqliteSaver.from_conn_string(db_path)
    builder = build_graph()
    graph = builder.compile(checkpointer=checkpointer)
    logger.info("LangGraph compiled with SQLite checkpointer.")
    return graph

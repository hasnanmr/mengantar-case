"""
LangGraph state definition for the sales chatbot.
"""
from typing import Annotated, List, Literal, Optional
from pydantic import BaseModel
from langgraph.graph.message import add_messages


class ChatState(BaseModel):
    """State shared across all nodes in the LangGraph."""
    messages: Annotated[List, add_messages] = []
    current_stage: Literal[
        "greeting",
        "needs_assessment",
        "consultation",
        "social_proof",
        "promotion",
        "closing",
        "end",
    ] = "greeting"
    thread_id: str = ""
    user_needs: Optional[str] = None
    context: Optional[str] = None  # RAG context
    token_log: List[dict] = []

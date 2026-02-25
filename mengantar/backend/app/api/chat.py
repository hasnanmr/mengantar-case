"""
Chat API routes with SSE streaming.
"""
import json
import logging
import uuid
from typing import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from app.agents.graph import get_graph_with_checkpointer
from app.agents.state import ChatState

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


async def chat_stream_generator(message: str, thread_id: str) -> AsyncGenerator[str, None]:
    """Generate SSE events for the chat response."""
    try:
        graph = await get_graph_with_checkpointer()
        config = {"configurable": {"thread_id": thread_id}}

        # Get or initialize state
        current_state = await graph.aget_state(config)
        if current_state.values:
            state = ChatState(**current_state.values)
        else:
            state = ChatState(thread_id=thread_id)

        state = ChatState(
            messages=list(state.messages) + [HumanMessage(content=message)],
            current_stage=state.current_stage,
            thread_id=thread_id,
            user_needs=state.user_needs,
            context=state.context,
            token_log=list(state.token_log),
        )

        # Run the graph
        result = await graph.ainvoke(state, config=config)

        # Get the last AI message
        ai_messages = [
            m for m in result.get("messages", [])
            if hasattr(m, "type") and m.type == "ai"
        ] or result.get("messages", [])

        response_text = ""
        if ai_messages:
            response_text = ai_messages[-1].content

        # Stream response word by word for effect
        words = response_text.split(" ")
        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            event = {"type": "token", "content": chunk}
            yield f"data: {json.dumps(event)}\n\n"

        # Send token usage info
        token_log = result.get("token_log", [])
        if token_log:
            latest = token_log[-1]
            usage_event = {
                "type": "usage",
                "input_tokens": latest.get("input_tokens", 0),
                "output_tokens": latest.get("output_tokens", 0),
                "total_tokens": latest.get("total_tokens", 0),
            }
            yield f"data: {json.dumps(usage_event)}\n\n"

        # Send done event
        done_event = {
            "type": "done",
            "thread_id": thread_id,
            "stage": result.get("current_stage", ""),
        }
        yield f"data: {json.dumps(done_event)}\n\n"

    except Exception as e:
        logger.error(f"Stream error: {e}", exc_info=True)
        error_event = {"type": "error", "content": str(e)}
        yield f"data: {json.dumps(error_event)}\n\n"


@router.post("/")
async def chat(request: ChatRequest):
    """Handle a chat message and return SSE stream."""
    thread_id = request.thread_id or str(uuid.uuid4())
    return StreamingResponse(
        chat_stream_generator(request.message, thread_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Thread-Id": thread_id,
        },
    )

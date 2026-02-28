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
from app.core.langfuse_handler import get_langfuse_handler
from app.core.config import get_settings

settings = get_settings()

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


async def chat_stream_generator(message: str, thread_id: str) -> AsyncGenerator[str, None]:
    """Generate SSE events for the chat response."""
    try:
        async with get_graph_with_checkpointer() as graph:
            config = {"configurable": {"thread_id": thread_id}}

            # Get or initialize state
            current_state = await graph.aget_state(config)
            if current_state.values:
                state = ChatState(**current_state.values)
            else:
                state = ChatState(thread_id=thread_id)

            input_state = {
                "messages": [HumanMessage(content=message)],
                "thread_id": thread_id,
            }

            # Initialize Langfuse handler for graph-level tracing (v3: no constructor args)
            langfuse_handler = get_langfuse_handler()
            if langfuse_handler:
                config["callbacks"] = [langfuse_handler]
                # In Langfuse v3, session_id and tags are passed via metadata
                config["metadata"] = {
                    "langfuse_session_id": thread_id,
                    "langfuse_tags": ["graph_execution", settings.environment],
                }

            # Stream the graph execution
            # We use stream_mode="messages" to get tokens from the LLM
            async for event in graph.astream(
                input_state, 
                config=config, 
                stream_mode="messages"
            ):
                # event is a tuple of (message, metadata)
                msg, metadata = event
                
                print(f"DEBUG: msg.type={msg.type} msg_class={msg.__class__.__name__} content={repr(msg.content)}")
                # Only stream AI messages (prevent echoing HumanMessage)
                if msg.content and msg.type == "ai":
                    # Send token event
                    token_event = {"type": "token", "content": msg.content}
                    yield f"data: {json.dumps(token_event)}\n\n"

            # Final state check for usage and stage
            final_state = await graph.aget_state(config)
            result = final_state.values

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


@router.post("")
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

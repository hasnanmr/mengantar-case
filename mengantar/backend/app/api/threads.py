"""
Thread management API routes.
"""
import logging
import psycopg
import psycopg.rows
import uuid
from fastapi import APIRouter, HTTPException

from app.core.config import get_settings
from app.core.db import get_pool

router = APIRouter(prefix="/threads", tags=["threads"])
settings = get_settings()
logger = logging.getLogger(__name__)


@router.get("/")
async def list_threads():
    """List all chat threads from PostgreSQL (LangGraph checkpoints table)."""
    try:
        async with get_pool().connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SET search_path TO mengantar_test, public")
                await cur.execute(
                    "SELECT thread_id, MAX(checkpoint_id) as last_checkpoint "
                    "FROM checkpoints GROUP BY thread_id ORDER BY last_checkpoint DESC"
                )
                rows = await cur.fetchall()
        return {"threads": [{"thread_id": row[0], "last_checkpoint": row[1]} for row in rows]}
    except Exception as e:
        logger.error(f"Error listing threads: {e}")
        return {"threads": []}


@router.get("/{thread_id}")
async def get_thread(thread_id: str):
    """Get thread details and message history using LangGraph's aget_state.
    
    Uses a DEDICATED database connection (not from the pool) to avoid
    deadlocking with the shared pool used by list_threads and chat.
    """
    try:
        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
        from app.agents.graph import build_graph

        # Use a dedicated connection to avoid pool exhaustion/deadlock
        async with await psycopg.AsyncConnection.connect(
            settings.database_url,
            autocommit=True,
        ) as conn:
            checkpointer = AsyncPostgresSaver(conn)
            await checkpointer.setup()

            graph = build_graph().compile(checkpointer=checkpointer)
            config = {"configurable": {"thread_id": thread_id}}
            current_state = await graph.aget_state(config)

            if not current_state or not current_state.values:
                raise HTTPException(status_code=404, detail="Thread not found")

            values = current_state.values
            token_log = values.get("token_log", [])
            ai_idx = 0

            messages_out = []
            for msg in values.get("messages", []):
                role = "assistant" if msg.type == "ai" else "user"
                msg_data = {
                    "id": getattr(msg, "id", str(uuid.uuid4())),
                    "role": role,
                    "content": msg.content,
                    "timestamp": None,
                }
                
                # Attach token usage to assistant messages
                if role == "assistant" and ai_idx < len(token_log):
                    msg_data["tokenUsage"] = {
                        "input_tokens": token_log[ai_idx].get("input_tokens", 0),
                        "output_tokens": token_log[ai_idx].get("output_tokens", 0),
                        "total_tokens": token_log[ai_idx].get("total_tokens", 0),
                    }
                    ai_idx += 1
                    
                messages_out.append(msg_data)

            return {
                "thread_id": thread_id,
                "messages": messages_out,
                "stage": values.get("current_stage", "greeting"),
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching thread {thread_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{thread_id}")
async def delete_thread(thread_id: str):
    """Delete all checkpoints for a thread."""
    try:
        async with get_pool().connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SET search_path TO mengantar_test, public")
                await cur.execute(
                    "DELETE FROM checkpoints WHERE thread_id = %s",
                    (thread_id,),
                )
            await conn.commit()
        return {"message": f"Thread {thread_id} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting thread {thread_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

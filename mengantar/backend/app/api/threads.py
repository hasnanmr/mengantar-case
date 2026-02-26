"""
Thread management API routes.
"""
import logging
import psycopg
import psycopg.rows
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
    """Get thread details and message history."""
    try:
        async with get_pool().connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT checkpoint_id FROM checkpoints "
                    "WHERE thread_id = %s ORDER BY checkpoint_id DESC LIMIT 1",
                    (thread_id,),
                )
                row = await cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Thread not found")
        return {"thread_id": thread_id, "checkpoint_id": row[0]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching thread {thread_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{thread_id}")
async def delete_thread(thread_id: str):
    """Delete all checkpoints for a thread."""
    try:
        async with get_pool().connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "DELETE FROM checkpoints WHERE thread_id = %s",
                    (thread_id,),
                )
            await conn.commit()
        return {"message": f"Thread {thread_id} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting thread {thread_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

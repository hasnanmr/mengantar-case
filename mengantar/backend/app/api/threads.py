"""
Thread management API routes.
"""
import logging
import aiosqlite
from fastapi import APIRouter, HTTPException

from app.core.config import get_settings

router = APIRouter(prefix="/threads", tags=["threads"])
settings = get_settings()
logger = logging.getLogger(__name__)


@router.get("/")
async def list_threads():
    """List all chat threads from SQLite."""
    try:
        async with aiosqlite.connect(settings.sqlite_db_path) as db:
            # LangGraph SQLite checkpointer stores threads in 'checkpoints' table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    thread_id TEXT,
                    checkpoint_id TEXT,
                    parent_checkpoint_id TEXT,
                    data BLOB,
                    metadata BLOB,
                    PRIMARY KEY (thread_id, checkpoint_id)
                )
            """)
            async with db.execute(
                "SELECT thread_id, MAX(checkpoint_id) as last_checkpoint FROM checkpoints GROUP BY thread_id ORDER BY last_checkpoint DESC"
            ) as cursor:
                rows = await cursor.fetchall()
        return {"threads": [{"thread_id": row[0], "last_checkpoint": row[1]} for row in rows]}
    except Exception as e:
        logger.error(f"Error listing threads: {e}")
        return {"threads": []}


@router.get("/{thread_id}")
async def get_thread(thread_id: str):
    """Get thread details and message history."""
    try:
        async with aiosqlite.connect(settings.sqlite_db_path) as db:
            async with db.execute(
                "SELECT checkpoint_id, data FROM checkpoints WHERE thread_id = ? ORDER BY checkpoint_id DESC LIMIT 1",
                (thread_id,)
            ) as cursor:
                row = await cursor.fetchone()
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
        async with aiosqlite.connect(settings.sqlite_db_path) as db:
            await db.execute("DELETE FROM checkpoints WHERE thread_id = ?", (thread_id,))
            await db.commit()
        return {"message": f"Thread {thread_id} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting thread {thread_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

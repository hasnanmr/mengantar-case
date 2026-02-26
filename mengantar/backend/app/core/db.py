"""
Global database connection pool manager.
"""
import logging
from typing import Optional
from psycopg_pool import AsyncConnectionPool

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_pool: Optional[AsyncConnectionPool] = None

async def init_pool() -> None:
    """Initialize the asynchronous connection pool."""
    global _pool
    if _pool is None:
        logger.info("Initializing global database connection pool...")
        # min_size=1, max_size=10 is a reasonable default for multi-worker setup
        _pool = AsyncConnectionPool(
            conninfo=settings.database_url,
            min_size=1,
            max_size=10,
            kwargs={"autocommit": True}
        )
        await _pool.open()
        logger.info("Database connection pool initialized.")

async def close_pool() -> None:
    """Close the asynchronous connection pool."""
    global _pool
    if _pool is not None:
        logger.info("Closing global database connection pool...")
        await _pool.close()
        _pool = None
        logger.info("Database connection pool closed.")

def get_pool() -> AsyncConnectionPool:
    """Get the initialized pool instance. Raises an error if not initialized."""
    if _pool is None:
        raise RuntimeError("Database connection pool is not initialized. Call init_pool() first.")
    return _pool

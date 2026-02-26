"""
reset_db.py: Reset the PostgreSQL database back to baseline by dropping
all application tables. Useful during development/testing.

WARNING: This will PERMANENTLY DELETE all data. Use with caution.
"""
import asyncio
import psycopg
from app.core.config import get_settings


async def reset_database():
    settings = get_settings()
    db_url = settings.database_url

    print(f"Connecting to database: {db_url}")
    try:
        async with await psycopg.AsyncConnection.connect(db_url, autocommit=True) as conn:
            async with conn.cursor() as cur:
                # Drop LangGraph checkpoint tables (managed by library)
                tables_to_drop = [
                    "checkpoint_writes",
                    "checkpoint_blobs",
                    "checkpoints",
                    "checkpoint_migrations",
                ]
                for table in tables_to_drop:
                    await cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                    print(f"Dropped table: {table}")

                # Drop application tables in mengantar_test schema
                await cur.execute("DROP TABLE IF EXISTS mengantar_test.testimonials CASCADE")
                print("Dropped table: mengantar_test.testimonials")

        print("Database reset complete. Run 'uv run alembic upgrade head' to recreate schema.")
    except Exception as e:
        print(f"Error resetting database: {e}")


if __name__ == "__main__":
    asyncio.run(reset_database())

import asyncio
import psycopg
import os
from app.core.config import get_settings

async def test_migration():
    settings = get_settings()
    db_url = os.getenv("DATABASE_URL", settings.database_url)
    
    # psycopg (v3) needs postgresql:// NOT postgresql+psycopg://
    if "+psycopg" in db_url:
        db_url = db_url.replace("+psycopg", "")

    print(f"Testing connection to: {db_url}")
    
    try:
        # Connect to verify database is reachable
        async with await psycopg.AsyncConnection.connect(db_url) as conn:
            print("Successfully connected to PostgreSQL.")
            
            async with conn.cursor() as cur:
                # Check for Alembic version table
                await cur.execute("SELECT table_name FROM information_schema.tables WHERE table_name = 'alembic_version'")
                row = await cur.fetchone()
                if row:
                    await cur.execute("SELECT version_num FROM alembic_version")
                    version = await cur.fetchone()
                    print(f"Current migration version: {version[0]}")
                else:
                    print("alembic_version table not found. Migrations may not have been run.")

                # Check for testimonials table
                await cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'mengantar_test' AND table_name = 'testimonials'")
                row = await cur.fetchone()
                if row:
                    print("Table 'mengantar_test.testimonials' exists.")
                else:
                    print("Table 'mengantar_test.testimonials' NOT found.")

                # Check for LangGraph tables
                await cur.execute("SELECT table_name FROM information_schema.tables WHERE table_name = 'checkpoints'")
                row = await cur.fetchone()
                if row:
                    print("Table 'checkpoints' exists (LangGraph).")
                else:
                    print("Table 'checkpoints' NOT found.")

    except Exception as e:
        print(f"Migration test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_migration())

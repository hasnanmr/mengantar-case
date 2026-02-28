# Persistence & Thread Checkpoints

This document explains how conversation state is persisted across interactions.

## LangGraph Checkpointers

We use LangGraph's built-in checkpointer system to save the state of each conversation thread.

- **Database**: PostgreSQL 17 is used for persistent storage and thread checkpointing.
- **Thread IDs**: Each user or session is assigned a unique `thread_id`.
- **Checkpointing**: The system automatically saves the state after each node execution, allowing the conversation to resume seamlessly.

## Configuration

The checkpointer is initialized in the backend and passed to the LangGraph `compile()` method.

> [!IMPORTANT]
> We use `AsyncPostgresSaver` to support asynchronous operations in the graph. This is initialized with an active PostgreSQL connection.

```python
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
import psycopg

# Initialize with PostgreSQL connection
async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
    checkpointer = AsyncPostgresSaver(conn)
    await checkpointer.setup()
    graph = builder.compile(checkpointer=checkpointer)
```

## Schema Management

We use **Alembic** for database migrations to manage the schema consistently.

- **Infrastructure**: The `000-infra` migration creates the `mengantar_test` schema.
- **App Data**: The `020-user` migration creates the `testimonials` table.
- **LangGraph**: The `060-checkpoint` migration ensures permissions are set for LangGraph's internal tables.

> [!NOTE]
> LangGraph manages its own internal tables (`checkpoints`, `checkpoint_blobs`, etc.) via `AsyncPostgresSaver.setup()`. In this project, these tables are created within the **`mengantar_test`** schema.

### Resetting the Database

To clear all conversation history and application data, you can use the provided reset script:

```bash
# from the backend directory
python scripts/reset_db.py
```

> [!WARNING]
> Running the reset script will drop the tables and clear all data. You will need to run `alembic upgrade head` again to recreate the schema.

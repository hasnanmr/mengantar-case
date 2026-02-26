"""060-checkpoint: LangGraph checkpoint tables setup.

Revision ID: c2749ce23a0f
Revises: 201cd6697fab
Create Date: 2026-02-26

IMPORTANT: LangGraph manages its own internal table schema via
AsyncPostgresSaver.setup(). This migration does NOT manually create those tables
to avoid redundancy or schema conflicts as the library evolves.

Instead, this migration records that the application requires LangGraph's
checkpoint tables to be initialized, and grants the necessary permissions on
the public schema where LangGraph creates its tables by default.

AsyncPostgresSaver.setup() is called at application startup (in graph.py) and
will create/migrate its own tables (checkpoints, checkpoint_blobs,
checkpoint_writes, checkpoint_migrations) idempotently.
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'c2749ce23a0f'
down_revision = '201cd6697fab'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Grant permissions on the public schema so LangGraph can create
    # its checkpoint tables there (it uses the public schema by default).
    op.execute("GRANT ALL ON SCHEMA public TO postgres")
    op.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO postgres")
    op.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO postgres")


def downgrade() -> None:
    # LangGraph tables in public are managed by the library itself.
    # No manual drop is performed here to avoid accidentally destroying
    # checkpoint data during a partial rollback.
    pass

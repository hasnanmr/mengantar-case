"""000-infra: Create mengantar_test schema and enable extensions.

Revision ID: 7e2061642423
Revises:
Create Date: 2026-02-26

This migration creates the application schema and enables required PostgreSQL
extensions. These are pre-conditions for all subsequent migrations.
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '7e2061642423'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create the application schema
    op.execute("CREATE SCHEMA IF NOT EXISTS mengantar_test")

    # Enable required extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    # Set default search path for the database
    op.execute("ALTER DATABASE postgres SET search_path TO mengantar_test, public")

    # Grant permissions to postgres user
    op.execute("GRANT USAGE ON SCHEMA mengantar_test TO postgres")
    op.execute("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA mengantar_test TO postgres")
    op.execute("GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA mengantar_test TO postgres")
    op.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA mengantar_test GRANT ALL ON TABLES TO postgres")
    op.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA mengantar_test GRANT ALL ON SEQUENCES TO postgres")


def downgrade() -> None:
    # NOTE: Dropping the schema will cascade-delete all tables within it.
    # This is intentional for a complete rollback of the infra migration.
    op.execute("DROP SCHEMA IF EXISTS mengantar_test CASCADE")

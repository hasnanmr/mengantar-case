"""020-user: Create testimonials table.

Revision ID: 201cd6697fab
Revises: 7e2061642423
Create Date: 2026-02-26

Creates the testimonials table in the mengantar_test schema.
This replaces the runtime CREATE TABLE IF NOT EXISTS that was previously
done via aiosqlite in TestimonialStore.initialize_store().
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '201cd6697fab'
down_revision = '7e2061642423'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'testimonials',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('image_path', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('id'),
        schema='mengantar_test',
    )
    op.create_index(
        'ix_testimonials_id',
        'testimonials',
        ['id'],
        schema='mengantar_test',
    )


def downgrade() -> None:
    op.drop_index('ix_testimonials_id', table_name='testimonials', schema='mengantar_test')
    op.drop_table('testimonials', schema='mengantar_test')

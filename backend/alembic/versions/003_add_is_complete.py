"""Add is_complete flag to skills

Revision ID: 003
Revises: 002
Create Date: 2026-05-06
"""
from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("skills") as batch:
        batch.add_column(sa.Column("is_complete", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade():
    with op.batch_alter_table("skills") as batch:
        batch.drop_column("is_complete")

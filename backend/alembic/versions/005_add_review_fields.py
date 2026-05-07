"""Add review-wizard fields to skills

Revision ID: 005
Revises: 004
Create Date: 2026-05-06
"""
from alembic import op
import sqlalchemy as sa

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("skills") as batch:
        batch.add_column(sa.Column("where_to_use", sa.Text(), nullable=True))
        batch.add_column(sa.Column("why_to_use", sa.Text(), nullable=True))
        batch.add_column(sa.Column("how_to_use", sa.Text(), nullable=True))
        batch.add_column(sa.Column("is_in_use", sa.Boolean(), nullable=False, server_default=sa.false()))
        batch.add_column(sa.Column("used_at", sa.String(), nullable=True))


def downgrade():
    with op.batch_alter_table("skills") as batch:
        batch.drop_column("used_at")
        batch.drop_column("is_in_use")
        batch.drop_column("how_to_use")
        batch.drop_column("why_to_use")
        batch.drop_column("where_to_use")

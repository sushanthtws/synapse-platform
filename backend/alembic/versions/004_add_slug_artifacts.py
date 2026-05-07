"""Add slug + artifacts columns to skills

Revision ID: 004
Revises: 003
Create Date: 2026-05-06
"""
from alembic import op
import sqlalchemy as sa

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("skills") as batch:
        batch.add_column(sa.Column("slug", sa.String(), nullable=True))
        batch.add_column(sa.Column("artifacts", sa.Text(), nullable=True))
        batch.create_index("ix_skills_slug", ["slug"])


def downgrade():
    with op.batch_alter_table("skills") as batch:
        batch.drop_index("ix_skills_slug")
        batch.drop_column("artifacts")
        batch.drop_column("slug")

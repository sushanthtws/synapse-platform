"""Initial schema

Revision ID: 001
Create Date: 2026-04-29
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("skills",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("title", sa.String), sa.Column("summary", sa.Text),
        sa.Column("domain", sa.String), sa.Column("usage", sa.String),
        sa.Column("difficulty", sa.String), sa.Column("tags", sa.Text),
        sa.Column("tools", sa.Text), sa.Column("languages", sa.Text),
        sa.Column("tech_stack", sa.Text), sa.Column("key_points", sa.Text),
        sa.Column("repo_path", sa.String), sa.Column("raw_content", sa.Text),
    )
    op.create_table("users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("email", sa.String, unique=True), sa.Column("name", sa.String),
        sa.Column("hashed_password", sa.String),
    )
    op.create_table("projects",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String), sa.Column("description", sa.String),
        sa.Column("owner_id", sa.Integer),
    )


def downgrade():
    op.drop_table("projects")
    op.drop_table("users")
    op.drop_table("skills")

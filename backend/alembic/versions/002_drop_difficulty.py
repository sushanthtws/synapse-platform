"""Drop difficulty column from skills

Revision ID: 002
Revises: 001
Create Date: 2026-05-06
"""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("skills") as batch:
        batch.drop_column("difficulty")


def downgrade():
    with op.batch_alter_table("skills") as batch:
        batch.add_column(sa.Column("difficulty", sa.String(), nullable=True))

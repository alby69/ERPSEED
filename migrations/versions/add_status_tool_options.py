"""Add status and tool_options columns to sys_models

Revision ID: add_status_tool_options
Revises:
Create Date: 2026-03-04
"""

from alembic import op
import sqlalchemy as sa

revision = "add_status_tool_options"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "sys_models",
        sa.Column("status", sa.String(20), nullable=True, server_default="draft"),
    )
    op.add_column("sys_models", sa.Column("tool_options", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("sys_models", "tool_options")
    op.drop_column("sys_models", "status")

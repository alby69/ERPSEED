"""Add theme columns to projects

Revision ID: add_theme_cols
Revises: 5f7011d6b770
Create Date: 2026-02-25 07:35:00.000000

"""

from alembic import op
import sqlalchemy as sa

revision = "add_theme_cols"
down_revision = "5f7011d6b770"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("projects", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "primary_color",
                sa.String(length=20),
                nullable=True,
                server_default="#1677ff",
            )
        )
        batch_op.add_column(
            sa.Column("border_radius", sa.Integer(), nullable=True, server_default="6")
        )
        batch_op.add_column(
            sa.Column(
                "theme_mode",
                sa.String(length=20),
                nullable=True,
                server_default="light",
            )
        )


def downgrade():
    with op.batch_alter_table("projects", schema=None) as batch_op:
        batch_op.drop_column("theme_mode")
        batch_op.drop_column("border_radius")
        batch_op.drop_column("primary_color")

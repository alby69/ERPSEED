"""Add filters_config and layout columns

Revision ID: add_filters_config_layout
Revises: add_theme_cols
Create Date: 2026-02-26
"""

from alembic import op
import sqlalchemy as sa

revision = "add_filters_config_layout"
down_revision = "add_theme_cols"
branch_labels = None
depends_on = None


def upgrade():
    # Use SQLAlchemy inspector to check for columns in a DB-agnostic way
    from sqlalchemy import inspect
    connection = op.get_bind()
    inspector = inspect(connection)

    # Aggiungi filters_config a sys_charts (solo se non esiste)
    columns = [c['name'] for c in inspector.get_columns('sys_charts')]
    if 'filters_config' not in columns:
        op.add_column(
            "sys_charts", sa.Column("filters_config", sa.JSON(), nullable=True)
        )

    # Aggiungi layout a sys_dashboards (solo se non esiste)
    columns = [c['name'] for c in inspector.get_columns('sys_dashboards')]
    if 'layout' not in columns:
        op.add_column("sys_dashboards", sa.Column("layout", sa.Text(), nullable=True))


def downgrade():
    pass

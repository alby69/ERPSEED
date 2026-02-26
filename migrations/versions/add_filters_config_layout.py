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
    # Aggiungi filters_config a sys_charts (solo se non esiste)
    connection = op.get_bind()
    result = connection.execute(
        sa.text("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'sys_charts' AND column_name = 'filters_config'
    """)
    )
    if result.fetchone() is None:
        op.add_column(
            "sys_charts", sa.Column("filters_config", sa.JSON(), nullable=True)
        )

    # Aggiungi layout a sys_dashboards (solo se non esiste)
    result = connection.execute(
        sa.text("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'sys_dashboards' AND column_name = 'layout'
    """)
    )
    if result.fetchone() is None:
        op.add_column("sys_dashboards", sa.Column("layout", sa.Text(), nullable=True))


def downgrade():
    pass

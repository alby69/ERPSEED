"""Add extended fields to SysModel and SysField for ERP-grade meta-model

This migration adds:
- SysModel: technical_name, table_name, module_id, is_system, is_active
- SysField: technical_name, is_index, is_active, relation_model, relation_type,
            relation_field, ui_widget, ui_placeholder, ui_group, ui_order,
            ui_visible, ui_readonly, ui_searchable, ui_filterable,
            is_computed, compute_script, depends_on, validation_min,
            validation_max, help_text

Revision ID: add_sysmodel_sysfield_extended
Revises: add_status_tool_options
Create Date: 2026-03-05
"""

from alembic import op
import sqlalchemy as sa

revision = "add_sysmodel_sysfield_extended"
down_revision = "add_status_tool_options"
branch_labels = None
depends_on = None


def upgrade():
    # SysModel new columns
    op.add_column(
        "sys_models",
        sa.Column("technical_name", sa.String(80), nullable=False, server_default=""),
    )
    op.add_column(
        "sys_models",
        sa.Column("table_name", sa.String(100), nullable=False, server_default=""),
    )
    op.add_column(
        "sys_models",
        sa.Column(
            "module_id", sa.Integer(), sa.ForeignKey("modules.id"), nullable=True
        ),
    )
    op.add_column(
        "sys_models",
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default="0"),
    )
    op.add_column(
        "sys_models",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
    )

    # SysField new columns
    op.add_column(
        "sys_fields",
        sa.Column("technical_name", sa.String(80), nullable=False, server_default=""),
    )
    op.add_column(
        "sys_fields",
        sa.Column("is_index", sa.Boolean(), nullable=False, server_default="0"),
    )
    op.add_column(
        "sys_fields",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
    )
    op.add_column(
        "sys_fields",
        sa.Column("relation_model", sa.String(80), nullable=True),
    )
    op.add_column(
        "sys_fields",
        sa.Column("relation_type", sa.String(20), nullable=True),
    )
    op.add_column(
        "sys_fields",
        sa.Column("relation_field", sa.String(80), nullable=True),
    )
    op.add_column(
        "sys_fields",
        sa.Column("ui_widget", sa.String(50), nullable=True),
    )
    op.add_column(
        "sys_fields",
        sa.Column("ui_placeholder", sa.String(255), nullable=True),
    )
    op.add_column(
        "sys_fields",
        sa.Column("ui_group", sa.String(80), nullable=True),
    )
    op.add_column(
        "sys_fields",
        sa.Column("ui_order", sa.Integer(), nullable=True, server_default="0"),
    )
    op.add_column(
        "sys_fields",
        sa.Column("ui_visible", sa.Boolean(), nullable=False, server_default="1"),
    )
    op.add_column(
        "sys_fields",
        sa.Column("ui_readonly", sa.Boolean(), nullable=False, server_default="0"),
    )
    op.add_column(
        "sys_fields",
        sa.Column("ui_searchable", sa.Boolean(), nullable=False, server_default="1"),
    )
    op.add_column(
        "sys_fields",
        sa.Column("ui_filterable", sa.Boolean(), nullable=False, server_default="1"),
    )
    op.add_column(
        "sys_fields",
        sa.Column("is_computed", sa.Boolean(), nullable=False, server_default="0"),
    )
    op.add_column(
        "sys_fields",
        sa.Column("compute_script", sa.Text(), nullable=True),
    )
    op.add_column(
        "sys_fields",
        sa.Column("depends_on", sa.String(255), nullable=True),
    )
    op.add_column(
        "sys_fields",
        sa.Column("validation_min", sa.Float(), nullable=True),
    )
    op.add_column(
        "sys_fields",
        sa.Column("validation_max", sa.Float(), nullable=True),
    )
    op.add_column(
        "sys_fields",
        sa.Column("help_text", sa.Text(), nullable=True),
    )


def downgrade():
    # SysField columns to drop
    op.drop_column("sys_fields", "help_text")
    op.drop_column("sys_fields", "validation_max")
    op.drop_column("sys_fields", "validation_min")
    op.drop_column("sys_fields", "depends_on")
    op.drop_column("sys_fields", "compute_script")
    op.drop_column("sys_fields", "is_computed")
    op.drop_column("sys_fields", "ui_filterable")
    op.drop_column("sys_fields", "ui_searchable")
    op.drop_column("sys_fields", "ui_readonly")
    op.drop_column("sys_fields", "ui_visible")
    op.drop_column("sys_fields", "ui_order")
    op.drop_column("sys_fields", "ui_group")
    op.drop_column("sys_fields", "ui_placeholder")
    op.drop_column("sys_fields", "ui_widget")
    op.drop_column("sys_fields", "relation_field")
    op.drop_column("sys_fields", "relation_type")
    op.drop_column("sys_fields", "relation_model")
    op.drop_column("sys_fields", "is_active")
    op.drop_column("sys_fields", "is_index")
    op.drop_column("sys_fields", "technical_name")

    # SysModel columns to drop
    op.drop_column("sys_models", "is_active")
    op.drop_column("sys_models", "is_system")
    op.drop_column("sys_models", "module_id")
    op.drop_column("sys_models", "table_name")
    op.drop_column("sys_models", "technical_name")

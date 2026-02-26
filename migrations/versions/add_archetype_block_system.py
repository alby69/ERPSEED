"""Add Archetype, Component, Block, and Marketplace tables

Revision ID: add_archetype_block_system
Revises: add_filters_config_layout
Create Date: 2026-02-26
"""

from alembic import op
import sqlalchemy as sa

revision = "add_archetype_block_system"
down_revision = "add_filters_config_layout"
branch_labels = None
depends_on = None


def upgrade():
    # === BUILDER TABLES ===

    # Archetypes table
    op.create_table(
        "archetypes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("component_type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("default_config", sa.JSON(), nullable=True),
        sa.Column("api_schema", sa.JSON(), nullable=True),
        sa.Column("icon", sa.String(length=50), nullable=True),
        sa.Column("preview_url", sa.String(length=255), nullable=True),
        sa.Column("is_system", sa.Boolean(), nullable=True),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["archetypes.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # Components table
    op.create_table(
        "components",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("archetype_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("config", sa.JSON(), nullable=True),
        sa.Column("position_x", sa.Integer(), nullable=True),
        sa.Column("position_y", sa.Integer(), nullable=True),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=True),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("block_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
        ),
        sa.ForeignKeyConstraint(
            ["archetype_id"],
            ["archetypes.id"],
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["components.id"],
        ),
        sa.ForeignKeyConstraint(
            ["block_id"],
            ["blocks.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Blocks table
    op.create_table(
        "blocks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("component_ids", sa.JSON(), nullable=True),
        sa.Column("relationships", sa.JSON(), nullable=True),
        sa.Column("api_endpoints", sa.JSON(), nullable=True),
        sa.Column("version", sa.String(length=20), nullable=True),
        sa.Column("test_suite_id", sa.Integer(), nullable=True),
        sa.Column("quality_score", sa.Integer(), nullable=True),
        sa.Column("is_certified", sa.Boolean(), nullable=True),
        sa.Column("certification_date", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["test_suite_id"],
            ["test_suites.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Block Relationships table
    op.create_table(
        "block_relationships",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("block_id", sa.Integer(), nullable=False),
        sa.Column("source_component_id", sa.Integer(), nullable=True),
        sa.Column("target_component_id", sa.Integer(), nullable=True),
        sa.Column("relationship_type", sa.String(length=50), nullable=True),
        sa.Column("config", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["block_id"],
            ["blocks.id"],
        ),
        sa.ForeignKeyConstraint(
            ["source_component_id"],
            ["components.id"],
        ),
        sa.ForeignKeyConstraint(
            ["target_component_id"],
            ["components.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # === MARKETPLACE TABLES ===

    # Marketplace Categories
    op.create_table(
        "marketplace_categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("icon", sa.String(length=50), nullable=True),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["marketplace_categories.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    # Marketplace Listings
    op.create_table(
        "marketplace_listings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("block_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("long_description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=True),
        sa.Column("thumbnail_url", sa.String(length=255), nullable=True),
        sa.Column("screenshots", sa.JSON(), nullable=True),
        sa.Column("demo_url", sa.String(length=255), nullable=True),
        sa.Column("downloads", sa.Integer(), nullable=True),
        sa.Column("rating_sum", sa.Integer(), nullable=True),
        sa.Column("rating_count", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("current_version", sa.String(length=20), nullable=True),
        sa.Column("changelog", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["block_id"],
            ["blocks.id"],
        ),
        sa.ForeignKeyConstraint(
            ["author_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["marketplace_categories.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    # Marketplace Reviews
    op.create_table(
        "marketplace_reviews",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("listing_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("is_verified_purchase", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["listing_id"],
            ["marketplace_listings.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Marketplace Payments
    op.create_table(
        "marketplace_payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("listing_id", sa.Integer(), nullable=False),
        sa.Column("buyer_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("payment_method", sa.String(length=50), nullable=True),
        sa.Column("transaction_id", sa.String(length=255), nullable=True),
        sa.Column("payment_data", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["listing_id"],
            ["marketplace_listings.id"],
        ),
        sa.ForeignKeyConstraint(
            ["buyer_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Marketplace Authors
    op.create_table(
        "marketplace_authors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False, unique=True),
        sa.Column("display_name", sa.String(length=120), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("avatar_url", sa.String(length=255), nullable=True),
        sa.Column("website", sa.String(length=255), nullable=True),
        sa.Column("total_downloads", sa.Integer(), nullable=True),
        sa.Column("total_revenue", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("avg_rating", sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    # Create indexes
    op.create_index("ix_components_project_id", "components", ["project_id"])
    op.create_index("ix_components_archetype_id", "components", ["archetype_id"])
    op.create_index("ix_components_block_id", "components", ["block_id"])
    op.create_index("ix_blocks_project_id", "blocks", ["project_id"])
    op.create_index(
        "ix_block_relationships_block_id", "block_relationships", ["block_id"]
    )
    op.create_index(
        "ix_marketplace_listings_author_id", "marketplace_listings", ["author_id"]
    )
    op.create_index(
        "ix_marketplace_listings_category_id", "marketplace_listings", ["category_id"]
    )
    op.create_index(
        "ix_marketplace_reviews_listing_id", "marketplace_reviews", ["listing_id"]
    )


def downgrade():
    op.drop_index("ix_marketplace_reviews_listing_id", "marketplace_reviews")
    op.drop_index("ix_marketplace_listings_category_id", "marketplace_listings")
    op.drop_index("ix_marketplace_listings_author_id", "marketplace_listings")
    op.drop_index("ix_block_relationships_block_id", "block_relationships")
    op.drop_index("ix_blocks_project_id", "blocks")
    op.drop_index("ix_components_block_id", "components")
    op.drop_index("ix_components_archetype_id", "components")
    op.drop_index("ix_components_project_id", "components")

    op.drop_table("marketplace_authors")
    op.drop_table("marketplace_payments")
    op.drop_table("marketplace_reviews")
    op.drop_table("marketplace_listings")
    op.drop_table("marketplace_categories")
    op.drop_table("block_relationships")
    op.drop_table("blocks")
    op.drop_table("components")
    op.drop_table("archetypes")

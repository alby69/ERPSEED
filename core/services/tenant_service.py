"""
Tenant Service - Manages tenant lifecycle and provisioning.

Handles:
- Tenant creation with schema
- Schema isolation
- Cross-tenant queries
"""

import logging
from typing import Optional, List
from extensions import db
from core.models.tenant import Tenant
from core.services.tenant_context import TenantContext

logger = logging.getLogger(__name__)


class TenantService:
    """Service for tenant management."""

    @staticmethod
    def create_tenant(name: str, slug: str, **kwargs) -> Tenant:
        """Create a new tenant.

        Args:
            name: Tenant display name
            slug: URL-friendly slug (subdomain)
            **kwargs: Additional tenant fields

        Returns:
            Created tenant
        """
        tenant = Tenant(name=name, slug=slug, **kwargs)
        db.session.add(tenant)
        db.session.commit()

        # Create schema for tenant (PostgreSQL)
        try:
            TenantService.create_schema(tenant.schema_name)
        except Exception as e:
            logger.warning(f"Could not create schema for tenant {tenant.slug}: {e}")

        return tenant

    @staticmethod
    def create_schema(schema_name: str):
        """Create a PostgreSQL schema for a tenant.

        Note: This only works with PostgreSQL. SQLite uses file-based isolation.
        """
        # Check if we're using PostgreSQL
        from flask import current_app

        db_uri = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")

        if "postgresql" in db_uri:
            # Create schema
            db.session.execute(db.text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
            db.session.commit()
            logger.info(f"Created schema: {schema_name}")
        else:
            logger.debug(f"Using SQLite - schema not applicable")

    @staticmethod
    def drop_schema(schema_name: str):
        """Drop a tenant's schema."""
        from flask import current_app

        db_uri = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")

        if "postgresql" in db_uri:
            db.session.execute(db.text(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE"))
            db.session.commit()
            logger.info(f"Dropped schema: {schema_name}")

    @staticmethod
    def get_schema_for_tenant(tenant_id: int) -> Optional[str]:
        """Get the schema name for a tenant."""
        tenant = Tenant.query.get(tenant_id)
        return tenant.schema_name if tenant else None

    @staticmethod
    def set_search_path(schema_name: str):
        """Set PostgreSQL search path to tenant schema."""
        from flask import current_app

        db_uri = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")

        if "postgresql" in db_uri and schema_name:
            db.session.execute(db.text(f"SET search_path TO {schema_name}, public"))
            logger.debug(f"Set search_path to: {schema_name}")

    @staticmethod
    def reset_search_path():
        """Reset search path to default."""
        from flask import current_app

        db_uri = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")

        if "postgresql" in db_uri:
            db.session.execute(db.text("SET search_path TO public"))

    @staticmethod
    def execute_cross_tenant(query, target_schema: str = None):
        """Execute a query across all schemas (for reporting).

        This requires superuser privileges in PostgreSQL.
        """
        from flask import current_app

        db_uri = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")

        if "postgresql" not in db_uri:
            return query.all()

        # Get all active tenant schemas
        tenants = Tenant.query.filter_by(is_active=True).all()
        results = []

        for tenant in tenants:
            if target_schema and tenant.schema_name != target_schema:
                continue

            try:
                # Set search path temporarily
                old_path = db.session.execute(db.text("SHOW search_path")).scalar()
                TenantService.set_search_path(tenant.schema_name)

                # Execute query
                results.extend(query.all())

                # Restore search path
                db.session.execute(db.text(f"SET search_path TO {old_path}"))
            except Exception as e:
                logger.error(f"Error querying tenant {tenant.slug}: {e}")

        return results

    @staticmethod
    def get_tenant_stats(tenant_id: int) -> dict:
        """Get statistics for a tenant."""
        tenant = Tenant.query.get(tenant_id)
        if not tenant:
            return {}

        # Count users
        user_count = tenant.users.count()

        # Count projects
        from models import Project

        project_count = Project.query.filter_by(tenant_id=tenant_id).count()

        # Count records (approximation)
        # This could be expensive, so we might want to cache this

        return {
            "tenant_id": tenant.id,
            "tenant_name": tenant.name,
            "user_count": user_count,
            "project_count": project_count,
            "plan": tenant.plan,
            "is_active": tenant.is_active,
        }


class TenantQueryHelper:
    """Helper for tenant-aware queries."""

    @staticmethod
    def apply_tenant_filter(query, model_class):
        """Apply tenant filter to a query.

        Adds tenant_id filter if the model has a tenant_id column.
        """
        tenant_id = TenantContext.get_tenant_id()

        if tenant_id is None:
            return query

        # Check if model has tenant_id
        if hasattr(model_class, "tenant_id"):
            return query.filter(model_class.tenant_id == tenant_id)

        return query

    @staticmethod
    def get_tenant_tables() -> List[str]:
        """Get list of tables that should be tenant-isolated."""
        # These tables should always be filtered by tenant
        return [
            "users",
            "projects",
            "products",
            "sales_orders",
            "purchase_orders",
        ]

    @staticmethod
    def should_isolate(table_name: str) -> bool:
        """Check if a table should be tenant-isolated."""
        return table_name in TenantQueryHelper.get_tenant_tables()


# Helper functions
def get_current_tenant() -> Optional[Tenant]:
    """Get current tenant."""
    return TenantContext.get_tenant()


def get_current_tenant_id() -> Optional[int]:
    """Get current tenant ID."""
    return TenantContext.get_tenant_id()


def require_tenant(f):
    """Decorator to require a valid tenant."""
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        if not TenantContext.get_tenant():
            from flask import abort

            abort(403, description="Tenant not found")
        return f(*args, **kwargs)

    return decorated

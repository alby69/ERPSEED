"""
Tenant query filters - automatic multi-tenant filtering for SQLAlchemy queries.

NOTA: Questo file è deprecato. Usare backend/core/services/tenant/tenant_filter.py
"""
from flask import g
from sqlalchemy import event
from sqlalchemy.orm import Query
from backend.core.services.tenant import TenantContext


class TenantQueryFilter:
    """
    Automatically filters all queries by tenant.
    Applies to all models that inherit from BaseModel.
    """

    _enabled = True

    @staticmethod
    def init_app(app):
        """Register SQLAlchemy events."""
        event.listen(
            Query,
            'before_compile',
            TenantQueryFilter._add_tenant_filter
        )

    @staticmethod
    def enable():
        """Enable tenant filtering."""
        TenantQueryFilter._enabled = True

    @staticmethod
    def disable():
        """Disable tenant filtering (for system operations)."""
        TenantQueryFilter._enabled = False

    @staticmethod
    def _add_tenant_filter(query):
        """
        Adds tenant filter to all queries.
        """
        if not TenantQueryFilter._enabled:
            return query

        tenant_id = TenantContext.get_tenant_id()

        # If no tenant, don't filter (for system operations)
        if tenant_id is None:
            return query

        # Get all entities in the query using _filter_by_entity approach
        try:
            for entity in query._entities:
                mapper = entity
                if hasattr(mapper, 'local_columns'):
                    # Check if this entity has tenant_id column
                    for col in mapper.local_columns:
                        if col.key == 'tenant_id':
                            query = query.filter(mapper.c.tenant_id == tenant_id)
                            break
        except (AttributeError, TypeError):
            # Fallback: try to get entities from mapped entities
            try:
                for entity in query._mapper_entities:
                    mapper = entity.mapper
                    if hasattr(mapper.c, 'tenant_id'):
                        query = query.filter(mapper.c.tenant_id == tenant_id)
            except (AttributeError, TypeError):
                pass

        return query


class SoftDeleteFilter:
    """
    Automatically filters out soft-deleted records.
    """

    @staticmethod
    def init_app(app):
        event.listen(
            Query,
            'before_compile',
            SoftDeleteFilter._add_soft_delete_filter
        )

    @staticmethod
    def _add_soft_delete_filter(query):
        """Adds filter to exclude soft-deleted records."""
        try:
            for entity in query._entities:
                mapper = entity
                if hasattr(mapper, 'local_columns'):
                    for col in mapper.local_columns:
                        if col.key == 'deleted_at':
                            query = query.filter(mapper.c.deleted_at == None)
                            break
        except (AttributeError, TypeError):
            # Fallback
            try:
                for entity in query._mapper_entities:
                    mapper = entity.mapper
                    if hasattr(mapper.c, 'deleted_at'):
                        query = query.filter(mapper.c.deleted_at == None)
            except (AttributeError, TypeError):
                pass
        return query

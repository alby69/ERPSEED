"""
Tenant Filter - Filtri automatici per queries multi-tenant.

Questo modulo unifica la logica di:
- TenantContext: gestione contesto richiesta
- TenantQueryFilter: filtri automatici SQLAlchemy
- SoftDeleteFilter: cancellazione logica

Per使用时, importare da questo modulo:
    from backend.core.services.tenant import TenantContext, TenantFilter
"""
from flask import g
from functools import wraps
from typing import Optional, Any
from sqlalchemy import event
from sqlalchemy.orm import Query


class TenantContext:
    """
    Manages tenant context for the current request.
    Uses Flask g for thread-safe storage.

    UNIFICATO con TenantFilter per semplificare l'architettura.
    """

    TENANT_KEY = 'current_tenant'
    USER_KEY = 'current_user'

    @classmethod
    def get_tenant(cls):
        """Get current tenant."""
        return getattr(g, cls.TENANT_KEY, None)

    @classmethod
    def set_tenant(cls, tenant):
        """Set current tenant."""
        setattr(g, cls.TENANT_KEY, tenant)

    @classmethod
    def get_user(cls):
        """Get current user."""
        return getattr(g, cls.USER_KEY, None)

    @classmethod
    def set_user(cls, user):
        """Set current user."""
        setattr(g, cls.USER_KEY, user)

    @classmethod
    def get_tenant_id(cls) -> Optional[int]:
        """Get current tenant ID."""
        tenant = cls.get_tenant()
        return tenant.id if tenant else None

    @classmethod
    def get_user_id(cls) -> Optional[int]:
        """Get current user ID."""
        user = cls.get_user()
        return user.id if user else None

    @classmethod
    def clear(cls):
        """Clear context."""
        g.pop(cls.TENANT_KEY, None)
        g.pop(cls.USER_KEY, None)

    @classmethod
    def is_active(cls) -> bool:
        """Check if tenant context is active."""
        return cls.get_tenant_id() is not None


class TenantFilter:
    """
    Filtro automatico per queries multi-tenant.
    Si integra con TenantContext per applicare filtri automaticamente.
    """

    _enabled = True

    @staticmethod
    def init_app(app):
        """Registra gli eventi SQLAlchemy."""
        event.listen(
            Query,
            'before_compile',
            TenantFilter._add_tenant_filter
        )

    @staticmethod
    def enable():
        """Abilita il filtraggio tenant."""
        TenantFilter._enabled = True

    @staticmethod
    def disable():
        """Disabilita il filtraggio tenant (per operazioni di sistema)."""
        TenantFilter._enabled = False

    @staticmethod
    def _add_tenant_filter(query: Query) -> Query:
        """
        Aggiunge filtro tenant a tutte le query.
        """
        if not TenantFilter._enabled:
            return query

        tenant_id = TenantContext.get_tenant_id()

        # If no tenant, don't filter (for system operations)
        if tenant_id is None:
            return query

        # Get all entities in the query
        try:
            for entity in query._entities:
                mapper = entity
                if hasattr(mapper, 'local_columns'):
                    for col in mapper.local_columns:
                        if col.key == 'tenant_id':
                            query = query.filter(mapper.c.tenant_id == tenant_id)
                            break
        except (AttributeError, TypeError):
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
    Filtro per cancellazione logica (soft delete).
    Esclude automaticamente i record cancellati.
    """

    @staticmethod
    def init_app(app):
        event.listen(
            Query,
            'before_compile',
            SoftDeleteFilter._add_soft_delete_filter
        )

    @staticmethod
    def _add_soft_delete_filter(query: Query) -> Query:
        """Aggiunge filtro per escludere record cancellati."""
        try:
            for entity in query._entities:
                mapper = entity
                if hasattr(mapper, 'local_columns'):
                    for col in mapper.local_columns:
                        if col.key == 'deleted_at':
                            query = query.filter(mapper.c.deleted_at == None)
                            break
        except (AttributeError, TypeError):
            try:
                for entity in query._mapper_entities:
                    mapper = entity.mapper
                    if hasattr(mapper.c, 'deleted_at'):
                        query = query.filter(mapper.c.deleted_at == None)
            except (AttributeError, TypeError):
                pass
        return query


def tenant_required(f):
    """
    Decorator che richiede un tenant valido.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not TenantContext.get_tenant():
            from flask import abort
            abort(403, description="Tenant not found")
        return f(*args, **kwargs)
    return decorated


# Backward compatibility - re-export from tenant_context for existing imports
def get_current_tenant():
    """Helper per ottenere tenant corrente."""
    return TenantContext.get_tenant()


def get_current_user():
    """Helper per ottenere utente corrente."""
    return TenantContext.get_user()


def get_current_tenant_id():
    """Helper per ottenere ID tenant corrente."""
    return TenantContext.get_tenant_id()


def get_current_user_id():
    """Helper per ottenere ID utente corrente."""
    return TenantContext.get_user_id()

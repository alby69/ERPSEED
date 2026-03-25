"""
Tenant context management.
Manages the current tenant for each request (thread-safe).
"""
from flask import g
from functools import wraps


class TenantContext:
    """
    Manages tenant context for the current request.
    Uses Flask g for thread-safe storage.
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
    def get_tenant_id(cls):
        """Get current tenant ID."""
        tenant = cls.get_tenant()
        return tenant.id if tenant else None

    @classmethod
    def get_user_id(cls):
        """Get current user ID."""
        user = cls.get_user()
        return user.id if user else None

    @classmethod
    def clear(cls):
        """Clear context."""
        g.pop(cls.TENANT_KEY, None)
        g.pop(cls.USER_KEY, None)


def tenant_required(f):
    """
    Decorator that requires a valid tenant.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not TenantContext.get_tenant():
            from flask import abort
            abort(403, description="Tenant not found")
        return f(*args, **kwargs)
    return decorated


def get_current_tenant():
    """Helper to get current tenant."""
    return TenantContext.get_tenant()


def get_current_user():
    """Helper to get current user."""
    return TenantContext.get_user()


def get_current_tenant_id():
    """Helper to get current tenant ID."""
    return TenantContext.get_tenant_id()


def get_current_user_id():
    """Helper to get current user ID."""
    return TenantContext.get_user_id()

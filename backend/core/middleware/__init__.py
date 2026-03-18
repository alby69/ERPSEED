"""
Middleware package.
"""
from backend.core.middleware.tenant_middleware import TenantMiddleware, setup_tenant_middleware

__all__ = ['TenantMiddleware', 'setup_tenant_middleware']

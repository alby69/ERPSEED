"""
ERPSeed Core Module.

Provides:
- Multi-tenant support
- Authentication & Authorization
- User management
- Audit logging
"""
from core.models import BaseModel, TimestampMixin, Tenant, AuditLog
from models import User
from core.services import (
    TenantContext,
    AuthService,
    Permission,
    PermissionService,
    tenant_required,
    get_current_tenant,
    get_current_user,
    get_current_tenant_id,
    get_current_userId,
)
from core.middleware import TenantMiddleware, setup_tenant_middleware
from core.api import auth_bp, tenant_bp

__version__ = '1.0.0'

__all__ = [
    # Models
    'BaseModel',
    'TimestampMixin',
    'Tenant',
    'User',
    'AuditLog',
    # Services
    'TenantContext',
    'AuthService',
    'Permission',
    'PermissionService',
    # Helpers
    'tenant_required',
    'get_current_tenant',
    'get_current_user',
    'get_current_tenant_id',
    'get_current_userId',
    # Middleware
    'TenantMiddleware',
    'setup_tenant_middleware',
    # API
    'auth_bp',
    'tenant_bp',
]

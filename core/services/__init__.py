"""
Core services package.

Struttura:
- auth/: Servizi di autenticazione
  - auth_service.py: Servizio principale login/register
  - jwt_service.py: Gestione token JWT (nuovo)
  - permission_service.py: Gestione permessi
- tenant/: Servizi tenant
  - tenant_service.py: Gestione CRUD tenant
  - tenant_context.py: Contesto richiesta
  - query_filter.py: Filtri automatici
"""
from core.services.tenant_context import (
    TenantContext,
    tenant_required,
    get_current_tenant,
    get_current_user,
    get_current_tenant_id,
    get_current_userId,
)
from core.services.auth_service import AuthService
from core.services.permission_service import (
    Permission,
    PermissionService,
)
from core.services.auth.jwt_service import JWTService

__all__ = [
    'TenantContext',
    'tenant_required',
    'get_current_tenant',
    'get_current_user',
    'get_current_tenant_id',
    'get_current_userId',
    'AuthService',
    'JWTService',
    'Permission',
    'PermissionService',
]

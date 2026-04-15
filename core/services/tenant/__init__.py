"""
Tenant services package.
Contiene i servizi per la gestione dei tenant.

Struttura:
- tenant_service.py: Servizio principale per la gestione dei tenant (gia' esistente)
- tenant_context.py: Contesto del tenant per la richiesta corrente (legacy, usa tenant_filter.py)
- tenant_filter.py: Filtri automatici per queries + Context unificato

Esportazioni:
- TenantContext: Contesto unificato per tenant/user
- TenantFilter: Filtro automatico queries
- SoftDeleteFilter: Filtro cancellazione logica
- tenant_required: Decorator per richiedere tenant
"""
from core.services.tenant.tenant_filter import (
    TenantContext,
    TenantFilter,
    SoftDeleteFilter,
    tenant_required,
    get_current_tenant,
    get_current_user,
    get_current_tenant_id,
    get_current_userId,
)

__all__ = [
    'TenantContext',
    'TenantFilter',
    'SoftDeleteFilter',
    'tenant_required',
    'get_current_tenant',
    'get_current_user',
    'get_current_tenant_id',
    'get_current_userId',
]

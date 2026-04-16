"""
Interfaces Package - Service interfaces for dependency injection.
"""

from .i_crud_service import ICrudService, IAuthService, ITenantService

__all__ = [
    "ICrudService",
    "IAuthService",
    "ITenantService",
]

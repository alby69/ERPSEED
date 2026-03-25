"""
Core API package.
"""
from backend.core.api.auth import auth_bp
from backend.core.api.tenant import tenant_bp

__all__ = ['auth_bp', 'tenant_bp']

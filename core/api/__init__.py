"""
Core API package.
"""
from core.api.auth import auth_bp
from core.api.tenant import tenant_bp

__all__ = ['auth_bp', 'tenant_bp']

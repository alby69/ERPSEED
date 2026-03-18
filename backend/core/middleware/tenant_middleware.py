"""
Tenant middleware - extracts and sets tenant context for each request.
"""
from flask import request, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from backend.core.models import Tenant
from backend.core.services.tenant import TenantContext


class TenantMiddleware:
    """
    Middleware that:
    1. Extracts tenant from request
    2. Sets tenant context
    3. Automatically filters queries
    """
    
    @staticmethod
    def init_app(app):
        """Register middleware with Flask app."""
        app.before_request(TenantMiddleware._before_request)
        app.after_request(TenantMiddleware._after_request)
    
    @staticmethod
    def _before_request():
        """Run before each request."""
        # Clear previous context
        TenantContext.clear()
        
        # Extract tenant
        tenant = TenantMiddleware._extract_tenant()
        if tenant:
            TenantContext.set_tenant(tenant)
            
            # Extract user if authenticated
            user = TenantMiddleware._extract_user()
            if user:
                TenantContext.set_user(user)
    
    @staticmethod
    def _extract_tenant():
        """
        Extract tenant from various sources:
        1. X-Tenant-ID header (for API)
        2. Subdomain (for UI)
        3. JWT token
        """
        # Method 1: Explicit header (for API)
        tenant_id = request.headers.get('X-Tenant-ID')
        if tenant_id:
            try:
                tenant_id = int(tenant_id)
                return Tenant.query.filter_by(id=tenant_id, is_active=True).first()
            except (ValueError, TypeError):
                pass
        
        # Method 2: Subdomain (for UI)
        host = request.host
        if host and '.' in host and not host.startswith('localhost'):
            parts = host.split('.')
            if len(parts) >= 2:
                subdomain = parts[0]
                if subdomain not in ('www', 'api', 'admin', 'app'):
                    return Tenant.query.filter_by(slug=subdomain, is_active=True).first()
        
        # Method 3: From JWT if user is logged in
        try:
            if verify_jwt_in_request(optional=True):
                user_id = get_jwt_identity()
                if user_id:
                    # Lazy import to avoid circular dependency
                    from backend.models import User
                    user = User.query.get(int(user_id))
                    if user:
                        return user.tenant
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def _extract_user():
        """Extract current user from JWT."""
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            if user_id:
                # Lazy import to avoid circular dependency
                from backend.models import User
                return User.query.get(int(user_id))
        except Exception:
            pass
        return None
    
    @staticmethod
    def _after_request(response):
        """Run after each request."""
        # Add tenant headers for debugging
        tenant = TenantContext.get_tenant()
        if tenant:
            response.headers['X-Tenant-ID'] = str(tenant.id)
            response.headers['X-Tenant-Slug'] = tenant.slug
        return response


def setup_tenant_middleware(app):
    """Setup function for tenant middleware."""
    TenantMiddleware.init_app(app)

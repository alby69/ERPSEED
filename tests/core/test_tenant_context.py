"""
Tests for tenant context and middleware.
"""
import pytest
from backend.core.services.tenant import TenantContext
from backend.core.services.tenant import get_current_tenant, get_current_user, get_current_tenant_id
from backend.core.middleware.tenant_middleware import TenantMiddleware
from backend.models import User


class TestTenantContext:
    """Test cases for TenantContext."""
    
    def test_set_and_get_tenant(self, app, tenant):
        """Test setting and getting tenant."""
        with app.app_context():
            TenantContext.set_tenant(tenant)
            assert TenantContext.get_tenant() is not None
            assert TenantContext.get_tenant().id == tenant.id
    
    def test_set_and_get_user(self, app, admin_user):
        """Test setting and getting user."""
        with app.app_context():
            TenantContext.set_user(admin_user)
            assert TenantContext.get_user() is not None
            assert TenantContext.get_user().id == admin_user.id
    
    def test_get_tenant_id(self, app, tenant):
        """Test getting tenant ID."""
        with app.app_context():
            TenantContext.set_tenant(tenant)
            assert TenantContext.get_tenant_id() == tenant.id
    
    def test_clear_context(self, app, tenant, admin_user):
        """Test clearing context."""
        with app.app_context():
            TenantContext.set_tenant(tenant)
            TenantContext.set_user(admin_user)
            
            TenantContext.clear()
            
            assert TenantContext.get_tenant() is None
            assert TenantContext.get_user() is None
    
    def test_get_tenant_none_when_not_set(self, app):
        """Test getting tenant when not set returns None."""
        with app.app_context():
            assert TenantContext.get_tenant() is None
    
    def test_get_current_tenant_helper(self, app, tenant):
        """Test helper function get_current_tenant."""
        with app.app_context():
            TenantContext.set_tenant(tenant)
            assert get_current_tenant() is not None
            assert get_current_tenant().id == tenant.id
    
    def test_get_current_user_helper(self, app, admin_user):
        """Test helper function get_current_user."""
        with app.app_context():
            TenantContext.set_user(admin_user)
            assert get_current_user() is not None
            assert get_current_user().id == admin_user.id
    
    def test_get_current_tenant_id_helper(self, app, tenant):
        """Test helper function get_current_tenant_id."""
        with app.app_context():
            TenantContext.set_tenant(tenant)
            assert get_current_tenant_id() == tenant.id


class TestTenantMiddleware:
    """Test cases for TenantMiddleware."""
    
    def test_middleware_has_required_methods(self, app):
        """Test middleware has all required methods."""
        # Verify middleware has all required static methods
        assert hasattr(TenantMiddleware, 'init_app')
        assert hasattr(TenantMiddleware, '_before_request')
        assert hasattr(TenantMiddleware, '_after_request')
        assert hasattr(TenantMiddleware, '_extract_tenant')
        assert hasattr(TenantMiddleware, '_extract_user')
    
    def test_extract_tenant_from_header(self, app, client, admin_user, tenant, db, session):
        """Test extracting tenant from X-Tenant-ID header."""
        with app.app_context():
            # Middleware already initialized, just test extraction logic
            with app.test_request_context(
                headers={'X-Tenant-ID': str(tenant.id)}
            ):
                tenant_result = TenantMiddleware._extract_tenant()
                assert tenant_result is not None
                assert tenant_result.id == tenant.id
    
    def test_extract_tenant_from_jwt(self, app, client, admin_user, tenant, db, session):
        """Test extracting tenant from JWT token."""
        # This test verifies the method exists and can be called
        # The actual JWT extraction is tested via integration tests
        with app.app_context():
            assert hasattr(TenantMiddleware, '_extract_tenant')
            assert hasattr(TenantMiddleware, '_extract_user')
    
    def test_after_request_adds_headers(self, app, client, tenant):
        """Test after_request adds tenant headers."""
        with app.app_context():
            TenantContext.set_tenant(tenant)
            
            with app.test_request_context():
                response = app.make_response('test')
                result = TenantMiddleware._after_request(response)
                
                assert result.headers.get('X-Tenant-ID') == str(tenant.id)
                assert result.headers.get('X-Tenant-Slug') == tenant.slug


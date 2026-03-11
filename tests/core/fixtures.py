"""
Mock utilities for testing.
Fornisce mock per TenantContext e altri servizi.
"""
from unittest.mock import MagicMock, patch
from typing import Optional, Any


class MockTenant:
    """Mock per Tenant."""
    
    def __init__(self, id: int = 1, name: str = "Test Tenant", slug: str = "test"):
        self.id = id
        self.name = name
        self.slug = slug
        self.is_active = True
        self.plan = "starter"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'is_active': self.is_active,
            'plan': self.plan
        }


class MockUser:
    """Mock per User."""
    
    def __init__(
        self, 
        id: int = 1, 
        email: str = "test@test.com",
        tenant_id: int = 1,
        role: str = "admin",
        is_primary: bool = True
    ):
        self.id = id
        self.email = email
        self.tenant_id = tenant_id
        self.role = role
        self.is_primary = is_primary
        self.is_active = True
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'tenant_id': self.tenant_id,
            'role': self.role,
            'is_primary': self.is_primary,
            'is_active': self.is_active
        }


class TenantContextMocker:
    """
    Context manager per mock del TenantContext nei test.
    
    Usage:
        with TenantContextMocker(tenant_id=1, user_id=1):
            # Test code here
            assert get_current_tenant_id() == 1
    """
    
    def __init__(self, tenant_id: Optional[int] = None, user_id: Optional[int] = None):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self._patches = []
    
    def __enter__(self):
        # Mock TenantContext methods
        if self.tenant_id is not None:
            mock_tenant = MockTenant(id=self.tenant_id)
            self._patches.append(
                patch('backend.core.services.tenant.TenantContext.get_tenant', 
                      return_value=mock_tenant)
            )
            self._patches.append(
                patch('backend.core.services.tenant.TenantContext.get_tenant_id', 
                      return_value=self.tenant_id)
            )
        
        if self.user_id is not None:
            mock_user = MockUser(id=self.user_id, tenant_id=self.tenant_id or 1)
            self._patches.append(
                patch('backend.core.services.tenant.TenantContext.get_user',
                      return_value=mock_user)
            )
            self._patches.append(
                patch('backend.core.services.tenant.TenantContext.get_user_id',
                      return_value=self.user_id)
            )
        
        for patch_obj in self._patches:
            patch_obj.start()
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        for patch_obj in self._patches:
            patch_obj.stop()


class AuthServiceMocker:
    """
    Mock per AuthService nei test.
    """
    
    @staticmethod
    def mock_login_success():
        """Mock login con successo."""
        return {
            'access_token': 'mock_access_token',
            'refresh_token': 'mock_refresh_token',
            'user': MockUser().to_dict()
        }
    
    @staticmethod
    def mock_login_failure():
        """Mock login con errore."""
        from unittest.mock import Mock
        mock = Mock()
        mock.login.side_effect = ValueError("Invalid credentials")
        return mock


__all__ = [
    'MockTenant',
    'MockUser', 
    'TenantContextMocker',
    'AuthServiceMocker',
]

"""
Unit tests for JWTService.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta


class TestJWTService:
    """Test cases for JWTService."""
    
    def test_build_user_claims(self):
        """Test building user claims."""
        from backend.core.services.auth.jwt_service import JWTService
        
        mock_user = MagicMock()
        mock_user.role = 'admin'
        mock_user.tenant_id = 1
        mock_user.email = 'test@test.com'
        mock_user.is_primary = True
        
        claims = JWTService.build_user_claims(mock_user)
        
        assert claims['role'] == 'admin'
        assert claims['tenant_id'] == 1
        assert claims['email'] == 'test@test.com'
        assert claims['is_primary'] is True
    
    def test_get_tenant_id_from_token_no_token(self):
        """Test getting tenant ID when no token present."""
        from backend.core.services.auth.jwt_service import JWTService
        
        with patch('backend.core.services.auth.jwt_service.get_jwt', return_value={}):
            result = JWTService.get_tenant_id_from_token()
            assert result is None
    
    def test_get_tenant_id_from_token_with_value(self):
        """Test getting tenant ID from token."""
        from backend.core.services.auth.jwt_service import JWTService
        
        with patch('backend.core.services.auth.jwt_service.get_jwt', return_value={'tenant_id': 5}):
            result = JWTService.get_tenant_id_from_token()
            assert result == 5
    
    def test_get_user_role_from_token(self):
        """Test getting user role from token."""
        from backend.core.services.auth.jwt_service import JWTService
        
        with patch('backend.core.services.auth.jwt_service.get_jwt', return_value={'role': 'manager'}):
            result = JWTService.get_user_role_from_token()
            assert result == 'manager'

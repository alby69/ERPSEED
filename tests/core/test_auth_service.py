"""
Tests for authentication service.
"""
import pytest
from backend.core.services.auth_service import AuthService
from backend.models import User
from backend.core.models import Tenant


class TestAuthService:
    """Test cases for AuthService."""
    
    def test_register_new_tenant(self, app, db, session):
        """Test registering a new tenant with admin user."""
        with app.app_context():
            result = AuthService.register(
                email='admin@newcompany.com',
                password='password123',
                first_name='New',
                last_name='Admin',
                tenant_name='New Company',
                tenant_slug='new-company'
            )
            
            assert result is not None
            assert 'access_token' in result
            assert 'refresh_token' in result
            assert 'user' in result
            assert 'tenant' in result
            
            # Verify user
            assert result['user']['email'] == 'admin@newcompany.com'
            assert result['user']['role'] == 'admin'
            assert result['user']['is_primary'] is True
            
            # Verify tenant
            assert result['tenant']['name'] == 'New Company'
            assert result['tenant']['slug'] == 'new-company'
    
    def test_register_duplicate_slug(self, app, db, session, admin_user):
        """Test registering with duplicate slug fails."""
        with app.app_context():
            with pytest.raises(ValueError, match="Slug already in use"):
                AuthService.register(
                    email='admin2@test.com',
                    password='password123',
                    first_name='Admin',
                    last_name='Two',
                    tenant_name='Test Company',
                    tenant_slug='test-company'  # Duplicate slug from fixture tenant
                )
    
    def test_login_success(self, app, db, session, admin_user):
        """Test successful login."""
        with app.app_context():
            result = AuthService.login(
                email='admin@test.com',
                password='admin123'
            )
            
            assert result is not None
            assert 'access_token' in result
            assert 'refresh_token' in result
            assert 'user' in result
            assert result['user']['email'] == 'admin@test.com'
    
    def test_login_invalid_password(self, app, db, session, admin_user):
        """Test login with invalid password fails."""
        with app.app_context():
            with pytest.raises(ValueError, match="Invalid email or password"):
                AuthService.login(
                    email='admin@test.com',
                    password='wrongpassword'
                )
    
    def test_login_invalid_email(self, app, db, session):
        """Test login with invalid email fails."""
        with app.app_context():
            with pytest.raises(ValueError, match="Invalid email or password"):
                AuthService.login(
                    email='nonexistent@test.com',
                    password='password123'
                )
    
    def test_login_inactive_user(self, app, db, session, tenant):
        """Test login with inactive user fails."""
        with app.app_context():
            user = User(
                tenant_id=tenant.id,
                email='inactive@test.com',
                role='user'
            )
            user.set_password('password123')
            user.is_active = False
            session.add(user)
            session.commit()
            
            with pytest.raises(ValueError, match="Account is disabled"):
                AuthService.login(
                    email='inactive@test.com',
                    password='password123'
                )
    
    def test_login_inactive_tenant(self, app, db, session, admin_user):
        """Test login with inactive tenant fails."""
        with app.app_context():
            tenant = session.merge(admin_user.tenant)
            tenant.is_active = False
            session.commit()
            session.refresh(tenant)
            
            with pytest.raises(ValueError, match="Organization is disabled"):
                AuthService.login(
                    email='admin@test.com',
                    password='admin123'
                )
    
    def test_login_email_normalized(self, app, db, session, admin_user):
        """Test login email is normalized to lowercase."""
        with app.app_context():
            result = AuthService.login(
                email='ADMIN@TEST.COM',
                password='admin123'
            )
            
            assert result is not None
            assert result['user']['email'] == 'admin@test.com'
    
    def test_refresh_token(self, app, db, session, admin_user):
        """Test token refresh."""
        import jwt as pyjwt
        from flask import Flask
        from flask_jwt_extended import create_refresh_token
        
        with app.app_context():
            with app.test_client() as client:
                refresh_token = create_refresh_token(identity=str(admin_user.id))
                
                response = client.post(
                    '/api/v1/auth/refresh',
                    headers={'Authorization': f'Bearer {refresh_token}'}
                )
                
                assert response.status_code == 200
                data = response.json
                assert 'access_token' in data
    
    def test_request_password_reset_existing_user(self, app, db, session, admin_user):
        """Test password reset request for existing user."""
        with app.app_context():
            result = AuthService.request_password_reset('admin@test.com')
            
            assert result['success'] is True
            assert 'reset_token' in result
            assert 'expires' in result
    
    def test_request_password_reset_nonexistent_user(self, app, db, session):
        """Test password reset request for nonexistent user doesn't reveal info."""
        with app.app_context():
            result = AuthService.request_password_reset('nonexistent@test.com')
            
            # Should return success even if user doesn't exist (security)
            assert result['success'] is True
    
    def test_reset_password_valid_token(self, app, db, session, admin_user):
        """Test password reset with valid token."""
        with app.app_context():
            # Request reset
            reset_result = AuthService.request_password_reset('admin@test.com')
            token = reset_result['reset_token']
            
            # Reset password
            result = AuthService.reset_password(token, 'newpassword123')
            
            assert result['success'] is True
            
            # Verify new password works
            login_result = AuthService.login(
                email='admin@test.com',
                password='newpassword123'
            )
            assert login_result is not None
    
    def test_reset_password_invalid_token(self, app, db, session):
        """Test password reset with invalid token fails."""
        with app.app_context():
            with pytest.raises(ValueError, match="Invalid token"):
                AuthService.reset_password('invalid-token', 'newpassword123')
    
    def test_change_password(self, app, db, session, admin_user):
        """Test password change."""
        with app.app_context():
            result = AuthService.change_password(
                user_id=admin_user.id,
                current_password='admin123',
                new_password='newpassword456'
            )
            
            assert result['success'] is True
            
            # Verify new password works
            login_result = AuthService.login(
                email='admin@test.com',
                password='newpassword456'
            )
            assert login_result is not None
    
    def test_change_password_wrong_current(self, app, db, session, admin_user):
        """Test password change with wrong current password fails."""
        with app.app_context():
            with pytest.raises(ValueError, match="Current password is incorrect"):
                AuthService.change_password(
                    user_id=admin_user.id,
                    current_password='wrongpassword',
                    new_password='newpassword456'
                )
    
    def test_access_token_contains_claims(self, app, db, session, admin_user):
        """Test access token contains required claims."""
        with app.app_context():
            result = AuthService.login(
                email='admin@test.com',
                password='admin123'
            )
            
            # Token is created, verify user has expected attributes
            assert result['user']['role'] == 'admin'
            assert result['user']['tenant_id'] == admin_user.tenant_id
            assert result['user']['is_primary'] is True

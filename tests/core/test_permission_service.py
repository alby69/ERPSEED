"""
Tests for permission service.
"""
import pytest
import json
from backend.core.services.permission_service import PermissionService, Permission, DEFAULT_ROLES
from backend.models import User


class TestPermissionService:
    """Test cases for PermissionService."""
    
    def test_admin_has_all_permissions(self, app, admin_user):
        """Test admin role has all permissions."""
        with app.app_context():
            assert PermissionService.has_permission(admin_user, Permission.MANAGE_USERS) is True
            assert PermissionService.has_permission(admin_user, Permission.VIEW_USERS) is True
            assert PermissionService.has_permission(admin_user, Permission.MANAGE_TENANT) is True
            assert PermissionService.has_permission(admin_user, Permission.VIEW_ALL) is True
            assert PermissionService.has_permission(admin_user, Permission.EDIT_ALL) is True
            assert PermissionService.has_permission(admin_user, Permission.DELETE_ALL) is True
    
    def test_primary_user_has_all_permissions(self, app, db, session, tenant):
        """Test primary user has all permissions."""
        with app.app_context():
            primary_user = User(
                tenant_id=tenant.id,
                email='primary@test.com',
                role='user',
                is_primary=True
            )
            primary_user.set_password('password123')
            session.add(primary_user)
            session.commit()
            
            assert PermissionService.has_permission(primary_user, Permission.MANAGE_USERS) is True
            assert PermissionService.has_permission(primary_user, Permission.MANAGE_TENANT) is True
    
    def test_manager_role_permissions(self, app, db, session, tenant):
        """Test manager role has correct permissions."""
        with app.app_context():
            manager_user = User(
                tenant_id=tenant.id,
                email='manager@test.com',
                role='manager'
            )
            manager_user.set_password('password123')
            session.add(manager_user)
            session.commit()
            
            assert PermissionService.has_permission(manager_user, Permission.VIEW_ALL) is True
            assert PermissionService.has_permission(manager_user, Permission.EDIT_ALL) is True
            assert PermissionService.has_permission(manager_user, Permission.MANAGE_SALES) is True
            assert PermissionService.has_permission(manager_user, Permission.MANAGE_USERS) is False
    
    def test_regular_user_permissions(self, app, db, session, tenant):
        """Test regular user role has correct permissions."""
        with app.app_context():
            regular_user = User(
                tenant_id=tenant.id,
                email='regular@test.com',
                role='user'
            )
            regular_user.set_password('password123')
            session.add(regular_user)
            session.commit()
            
            assert PermissionService.has_permission(regular_user, Permission.VIEW_SALES) is True
            assert PermissionService.has_permission(regular_user, Permission.MANAGE_SALES) is True
            assert PermissionService.has_permission(regular_user, Permission.VIEW_ALL) is False
    
    def test_viewer_role_permissions(self, app, db, session, tenant):
        """Test viewer role has correct permissions."""
        with app.app_context():
            viewer_user = User(
                tenant_id=tenant.id,
                email='viewer@test.com',
                role='viewer'
            )
            viewer_user.set_password('password123')
            session.add(viewer_user)
            session.commit()
            
            assert PermissionService.has_permission(viewer_user, Permission.VIEW_ALL) is True
            assert PermissionService.has_permission(viewer_user, Permission.EDIT_ALL) is False
            assert PermissionService.has_permission(viewer_user, Permission.MANAGE_SALES) is False
    
    def test_custom_role_permissions(self, app, db, session, tenant):
        """Test custom role with specific permissions."""
        with app.app_context():
            from backend.core.models.user import UserRole
            
            # Create custom role
            custom_role = UserRole(
                tenant_id=tenant.id,
                name='custom_role',
                permissions=json.dumps([Permission.VIEW_SALES, Permission.MANAGE_PRODUCTS]),
                is_default=False
            )
            session.add(custom_role)
            session.flush()
            
            # Create user with custom role
            custom_user = User(
                tenant_id=tenant.id,
                email='custom@test.com',
                role='user',
                custom_role_id=custom_role.id
            )
            custom_user.set_password('password123')
            session.add(custom_user)
            session.commit()
            
            assert PermissionService.has_permission(custom_user, Permission.VIEW_SALES) is True
            assert PermissionService.has_permission(custom_user, Permission.MANAGE_PRODUCTS) is True
            assert PermissionService.has_permission(custom_user, Permission.MANAGE_SALES) is False
    
    def test_has_any_permission(self, app, admin_user):
        """Test has_any_permission."""
        with app.app_context():
            assert PermissionService.has_any_permission(
                admin_user, 
                [Permission.MANAGE_USERS, Permission.MANAGE_TENANT]
            ) is True
            
            assert PermissionService.has_any_permission(
                admin_user,
                [Permission.MANAGE_SALES, Permission.MANAGE_PRODUCTS]
            ) is True
    
    def test_has_all_permissions(self, app, admin_user):
        """Test has_all_permissions."""
        with app.app_context():
            assert PermissionService.has_all_permissions(
                admin_user,
                [Permission.MANAGE_USERS, Permission.VIEW_USERS]
            ) is True
    
    def test_has_permission_none_user(self, app):
        """Test has_permission with None user returns False."""
        with app.app_context():
            assert PermissionService.has_permission(None, Permission.VIEW_ALL) is False
    
    def test_default_roles_structure(self):
        """Test default roles have correct structure."""
        assert 'admin' in DEFAULT_ROLES
        assert 'manager' in DEFAULT_ROLES
        assert 'user' in DEFAULT_ROLES
        assert 'viewer' in DEFAULT_ROLES
        
        assert Permission.MANAGE_USERS in DEFAULT_ROLES['admin']
        assert Permission.VIEW_ALL in DEFAULT_ROLES['viewer']


class TestPermissionConstants:
    """Test permission constants are defined correctly."""
    
    def test_user_permissions(self):
        """Test user permission constants."""
        assert Permission.MANAGE_USERS == 'manage_users'
        assert Permission.VIEW_USERS == 'view_users'
    
    def test_tenant_permissions(self):
        """Test tenant permission constants."""
        assert Permission.MANAGE_TENANT == 'manage_tenant'
        assert Permission.VIEW_TENANT == 'view_tenant'
    
    def test_data_permissions(self):
        """Test data permission constants."""
        assert Permission.VIEW_ALL == 'view_all'
        assert Permission.EDIT_ALL == 'edit_all'
        assert Permission.DELETE_ALL == 'delete_all'
    
    def test_module_permissions(self):
        """Test module permission constants."""
        assert Permission.VIEW_ACCOUNTING == 'view_accounting'
        assert Permission.MANAGE_ACCOUNTING == 'manage_accounting'
        assert Permission.VIEW_SALES == 'view_sales'
        assert Permission.MANAGE_SALES == 'manage_sales'
        assert Permission.VIEW_PRODUCTS == 'view_products'
        assert Permission.MANAGE_PRODUCTS == 'manage_products'
        assert Permission.VIEW_PARTIES == 'view_parties'
        assert Permission.MANAGE_PARTIES == 'manage_parties'

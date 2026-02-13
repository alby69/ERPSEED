"""
Tests for UserService.
"""
import pytest
from backend.services.user_service import UserService
from backend.models import User


class TestUserService:
    """Test cases for UserService."""
    
    def test_register_new_user(self, app, db, session):
        """Test registering a new user."""
        with app.app_context():
            service = UserService()
            
            user = service.register(
                email='newuser@test.com',
                password='password123',
                first_name='New',
                last_name='User'
            )
            
            assert user is not None
            assert user.email == 'newuser@test.com'
            assert user.first_name == 'New'
            assert user.last_name == 'User'
            assert user.check_password('password123')
    
    def test_register_duplicate_email(self, app, db, session, admin_user):
        """Test registering with duplicate email fails."""
        with app.app_context():
            service = UserService()
            
            from flask_smorest import abort
            with pytest.raises(Exception):
                service.register(
                    email='admin@test.com',
                    password='password123'
                )
    
    def test_get_by_id(self, app, db, session, admin_user):
        """Test getting user by ID."""
        with app.app_context():
            service = UserService()
            
            user = service.get_by_id(admin_user.id)
            
            assert user is not None
            assert user.email == 'admin@test.com'
    
    def test_get_by_id_not_found(self, app, db, session):
        """Test getting non-existent user returns None."""
        with app.app_context():
            service = UserService()
            
            user = service.get_by_id(99999)
            
            assert user is None
    
    def test_update_user(self, app, db, session, regular_user):
        """Test updating a user."""
        with app.app_context():
            service = UserService()
            
            updated = service.update(
                regular_user.id,
                {'first_name': 'Updated', 'last_name': 'Name'}
            )
            
            assert updated.first_name == 'Updated'
            assert updated.last_name == 'Name'
    
    def test_update_email_duplicate(self, app, db, session, admin_user, regular_user):
        """Test updating to existing email fails."""
        with app.app_context():
            service = UserService()
            
            from flask_smorest import abort
            with pytest.raises(Exception):
                service.update(
                    regular_user.id,
                    {'email': 'admin@test.com'}
                )
    
    def test_delete_user(self, app, db, session, admin_user, regular_user):
        """Test deleting a user."""
        with app.app_context():
            service = UserService()
            
            service.delete(regular_user.id, admin_user.id)
            
            user = service.get_by_id(regular_user.id)
            assert user is None
    
    def test_delete_own_account_fails(self, app, db, session, admin_user):
        """Test user cannot delete their own account."""
        with app.app_context():
            service = UserService()
            
            from flask_smorest import abort
            with pytest.raises(Exception):
                service.delete(admin_user.id, admin_user.id)
    
    def test_reset_password(self, app, db, session, regular_user):
        """Test admin can reset user password."""
        with app.app_context():
            service = UserService()
            
            message = service.reset_password(regular_user.id, 'newpassword')
            
            # Refresh from database
            session.expire_all()
            user = session.get(type(regular_user), regular_user.id)
            
            assert 'reset' in message.lower()
            assert user.check_password('newpassword')
            assert user.force_password_change is True
    
    def test_change_password(self, app, db, session, regular_user):
        """Test user can change their own password."""
        with app.app_context():
            service = UserService()
            
            service.change_password(
                regular_user.id,
                'user123',
                'newpassword456'
            )
            
            # Refresh from database
            session.expire_all()
            user = session.get(type(regular_user), regular_user.id)
            
            assert user.check_password('newpassword456')
    
    def test_change_password_wrong_current(self, app, db, session, regular_user):
        """Test changing password with wrong current password fails."""
        with app.app_context():
            service = UserService()
            
            from flask_smorest import abort
            with pytest.raises(Exception):
                service.change_password(
                    regular_user.id,
                    'wrongpassword',
                    'newpassword456'
                )
    
    def test_email_is_lowercase(self, app, db, session):
        """Test email is converted to lowercase."""
        with app.app_context():
            service = UserService()
            
            user = service.register(
                email='UPPERCASE@TEST.COM',
                password='password123'
            )
            
            assert user.email == 'uppercase@test.com'

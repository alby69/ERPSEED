"""
Tests for base models (BaseModel, Tenant, User, AuditLog).
"""
import pytest
from datetime import datetime
from backend.core.models.base import BaseModel, TimestampMixin
from backend.core.models.tenant import Tenant
from backend.core.models.audit import AuditLog
from backend.models import User


class TestBaseModel:
    """Test cases for BaseModel."""
    
    def test_to_dict(self, app, db, session, tenant):
        """Test model serialization to dict."""
        with app.app_context():
            user = User(
                tenant_id=tenant.id,
                email='test@test.com',
                role='user'
            )
            user.set_password('password')
            session.add(user)
            session.commit()
            
            user_dict = user.to_dict()
            
            assert 'id' in user_dict
            assert 'email' in user_dict
            assert 'created_at' in user_dict
            assert 'updated_at' in user_dict
    
    def test_to_dict_exclude(self, app, db, session, tenant):
        """Test to_dict with exclude parameter."""
        with app.app_context():
            user = User(
                tenant_id=tenant.id,
                email='test@test.com',
                role='user'
            )
            user.set_password('password')
            session.add(user)
            session.commit()
            
            user_dict = user.to_dict(exclude=['email'])
            
            assert 'id' in user_dict
            assert 'email' not in user_dict
    
    def test_soft_delete(self, app, db, session, tenant):
        """Test soft delete functionality."""
        with app.app_context():
            user = User(
                tenant_id=tenant.id,
                email='delete@test.com',
                role='user'
            )
            user.set_password('password')
            session.add(user)
            session.commit()
            user_id = user.id
            
            # Soft delete
            user.soft_delete()
            session.commit()
            
            # Check deleted_at is set
            session.refresh(user)
            assert user.deleted_at is not None
            assert user.is_deleted is True
    
    def test_restore(self, app, db, session, tenant):
        """Test restore soft-deleted record."""
        with app.app_context():
            user = User(
                tenant_id=tenant.id,
                email='restore@test.com',
                role='user'
            )
            user.set_password('password')
            session.add(user)
            session.commit()
            
            # Soft delete
            user.soft_delete()
            session.commit()
            
            # Restore
            user.restore()
            session.commit()
            
            session.refresh(user)
            assert user.deleted_at is None
            assert user.is_deleted is False


class TestTenantModel:
    """Test cases for Tenant model."""
    
    def test_tenant_creation(self, app, db, session):
        """Test creating a tenant."""
        with app.app_context():
            tenant = Tenant(
                name='Test Company',
                slug='test-company',
                email='admin@test.com',
                is_active=True
            )
            session.add(tenant)
            session.commit()
            
            assert tenant.id is not None
            assert tenant.name == 'Test Company'
            assert tenant.slug == 'test-company'
            assert tenant.is_active is True
    
    def test_tenant_default_values(self, app, db, session):
        """Test tenant default values."""
        with app.app_context():
            tenant = Tenant(
                name='Default Company',
                slug='default-company'
            )
            session.add(tenant)
            session.commit()
            
            assert tenant.country == 'IT'
            assert tenant.timezone == 'Europe/Rome'
            assert tenant.locale == 'it_IT'
            assert tenant.currency == 'EUR'
            assert tenant.plan == 'starter'
            assert tenant.max_users == 3
            assert tenant.max_storage_mb == 1024
            assert tenant.primary_color == '#3498db'
    
    def test_tenant_repr(self, app, db, session):
        """Test tenant __repr__."""
        with app.app_context():
            tenant = Tenant(
                name='Repr Company',
                slug='repr-company'
            )
            session.add(tenant)
            session.commit()
            
            assert repr(tenant) == '<Tenant repr-company>'
    
    def test_tenant_to_dict(self, app, db, session):
        """Test tenant serialization."""
        with app.app_context():
            tenant = Tenant(
                name='Dict Company',
                slug='dict-company',
                email='admin@dict.com'
            )
            session.add(tenant)
            session.commit()
            
            tenant_dict = tenant.to_dict()
            
            assert 'id' in tenant_dict
            assert 'name' in tenant_dict
            assert 'slug' in tenant_dict
            assert tenant_dict['name'] == 'Dict Company'
    
    def test_tenant_to_dict_include_config(self, app, db, session):
        """Test tenant serialization with config."""
        with app.app_context():
            tenant = Tenant(
                name='Config Company',
                slug='config-company',
                plan='business',
                max_users=10
            )
            session.add(tenant)
            session.commit()
            
            # Without config
            tenant_dict = tenant.to_dict()
            assert 'plan' not in tenant_dict
            
            # With config
            tenant_dict_full = tenant.to_dict(include_config=True)
            assert 'plan' in tenant_dict_full
            assert tenant_dict_full['plan'] == 'business'


class TestUserModel:
    """Test cases for User model."""
    
    def test_user_creation(self, app, db, session, tenant):
        """Test creating a user."""
        with app.app_context():
            user = User(
                tenant_id=tenant.id,
                email='test@test.com',
                role='admin'
            )
            user.set_password('password123')
            session.add(user)
            session.commit()
            
            assert user.id is not None
            assert user.email == 'test@test.com'
            assert user.role == 'admin'
            assert user.check_password('password123') is True
    
    def test_user_full_name(self, app, db, session, tenant):
        """Test user full name property."""
        with app.app_context():
            user = User(
                tenant_id=tenant.id,
                email='name@test.com',
                first_name='John',
                last_name='Doe'
            )
            session.add(user)
            session.commit()
            
            assert user.full_name == 'John Doe'
    
    def test_user_full_name_no_first_last(self, app, db, session, tenant):
        """Test user full name when first/last not set."""
        with app.app_context():
            user = User(
                tenant_id=tenant.id,
                email='email@test.com'
            )
            session.add(user)
            session.commit()
            
            assert user.full_name == 'email@test.com'
    
    def test_user_password_hash(self, app, db, session, tenant):
        """Test password hashing."""
        with app.app_context():
            user = User(
                tenant_id=tenant.id,
                email='hash@test.com',
                role='user'
            )
            user.set_password('mypassword')
            
            assert user.password_hash is not None
            assert user.password_hash != 'mypassword'
            assert user.check_password('mypassword') is True
            assert user.check_password('wrongpassword') is False
    
    def test_user_record_login(self, app, db, session, tenant):
        """Test login recording."""
        with app.app_context():
            user = User(
                tenant_id=tenant.id,
                email='login@test.com',
                role='user'
            )
            user.set_password('password')
            session.add(user)
            session.commit()
            
            initial_count = user.login_count
            
            user.record_login()
            session.commit()
            
            assert user.login_count == initial_count + 1
            assert user.last_login_at is not None
    
    def test_user_unique_constraint(self, app, db, session, tenant):
        """Test unique constraint on tenant + email."""
        with app.app_context():
            user1 = User(
                tenant_id=tenant.id,
                email='unique@test.com',
                role='user'
            )
            user1.set_password('password')
            session.add(user1)
            session.commit()
            
            # Try to create duplicate
            user2 = User(
                tenant_id=tenant.id,
                email='unique@test.com',
                role='user'
            )
            user2.set_password('password')
            session.add(user2)
            
            from sqlalchemy.exc import IntegrityError
            with pytest.raises(IntegrityError):
                session.commit()
    
    def test_user_force_password_change(self, app, db, session, tenant):
        """Test force password change flag."""
        with app.app_context():
            user = User(
                tenant_id=tenant.id,
                email='force@test.com',
                role='user'
            )
            user.set_password('password')
            
            assert user.force_password_change is False
            
            user.force_password_change = True
            session.add(user)
            session.commit()
            
            session.refresh(user)
            assert user.force_password_change is True


class TestAuditLogModel:
    """Test cases for AuditLog model."""
    
    def test_audit_log_creation(self, app, db, session, admin_user):
        """Test creating an audit log."""
        with app.app_context():
            log = AuditLog.log_create(
                user_id=admin_user.id,
                tenant_id=admin_user.tenant_id,
                resource_type='user',
                resource_id=admin_user.id,
                new_values={'action': 'create'}
            )
            session.commit()
            
            assert log.id is not None
            assert log.action == AuditLog.ACTION_CREATE
            assert log.resource_type == 'user'
            assert log.status == 'success'
    
    def test_audit_log_update(self, app, db, session, admin_user):
        """Test creating update audit log."""
        with app.app_context():
            log = AuditLog.log_update(
                user_id=admin_user.id,
                tenant_id=admin_user.tenant_id,
                resource_type='user',
                resource_id=admin_user.id,
                old_values={'name': 'Old'},
                new_values={'name': 'New'}
            )
            session.commit()
            
            assert log.action == AuditLog.ACTION_UPDATE
            assert log.changes is not None
    
    def test_audit_log_delete(self, app, db, session, admin_user):
        """Test creating delete audit log."""
        with app.app_context():
            log = AuditLog.log_delete(
                user_id=admin_user.id,
                tenant_id=admin_user.tenant_id,
                resource_type='user',
                resource_id=admin_user.id,
                old_values={'email': 'test@test.com'}
            )
            session.commit()
            
            assert log.action == AuditLog.ACTION_DELETE
    
    def test_audit_log_constants(self):
        """Test audit log action constants."""
        assert AuditLog.ACTION_CREATE == 'create'
        assert AuditLog.ACTION_UPDATE == 'update'
        assert AuditLog.ACTION_DELETE == 'delete'
        assert AuditLog.ACTION_LOGIN == 'login'
        assert AuditLog.ACTION_LOGOUT == 'logout'
        assert AuditLog.ACTION_PASSWORD_CHANGE == 'password_change'
        assert AuditLog.ACTION_PASSWORD_RESET == 'password_reset'
        assert AuditLog.ACTION_EXPORT == 'export'
        assert AuditLog.ACTION_IMPORT == 'import'
        assert AuditLog.ACTION_VIEW == 'view'
    
    def test_audit_log_to_dict(self, app, db, session, admin_user):
        """Test audit log serialization."""
        with app.app_context():
            log = AuditLog.log_create(
                user_id=admin_user.id,
                tenant_id=admin_user.tenant_id,
                resource_type='user',
                resource_id=admin_user.id
            )
            session.commit()
            
            log_dict = log.to_dict()
            
            assert 'id' in log_dict
            assert 'action' in log_dict
            assert 'resource_type' in log_dict

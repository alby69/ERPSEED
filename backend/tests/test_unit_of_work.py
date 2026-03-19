"""
Tests for Unit of Work Pattern.
"""
import pytest
import os
os.environ.setdefault('JWT_SECRET_KEY', 'test-secret-key-for-testing-purposes-only-12345')

from backend import create_app
from backend.extensions import db
from backend.models import Project, Tenant, User


class TestUnitOfWork:
    """Test cases for UnitOfWork pattern."""
    
    @pytest.fixture
    def app(self):
        """Create test app with in-memory database."""
        app = create_app(db_url="sqlite:///:memory:")
        app.config["TESTING"] = True
        with app.app_context():
            db.create_all()
            yield app
            db.session.remove()
            db.drop_all()
    
    def test_basic_commit(self, app):
        """Test basic transaction commit."""
        with app.app_context():
            from backend.shared.transaction import UnitOfWork
            
            with UnitOfWork(db) as uow:
                tenant = Tenant(name="Test Tenant", slug="test")
                db.session.add(tenant)
                uow.flush()
                
                user = User(
                    email="test@example.com",
                    password_hash="hash",
                    first_name="Test",
                    last_name="User",
                    tenant_id=tenant.id
                )
                db.session.add(user)
            
            assert Tenant.query.count() == 1
            assert User.query.count() == 1
    
    def test_rollback_on_exception(self, app):
        """Test automatic rollback when exception occurs."""
        with app.app_context():
            from backend.shared.transaction import UnitOfWork
            
            with pytest.raises(ValueError):
                with UnitOfWork(db) as uow:
                    tenant = Tenant(name="Test Tenant", slug="test")
                    db.session.add(tenant)
                    uow.flush()
                    raise ValueError("Test error")
            
            assert Tenant.query.count() == 0
    
    def test_nested_transactions(self, app):
        """Test nested UnitOfWork (should delegate to outer)."""
        with app.app_context():
            from backend.shared.transaction import UnitOfWork
            
            outer_committed = False
            
            with UnitOfWork(db) as outer:
                tenant = Tenant(name="Test Tenant", slug="test")
                db.session.add(tenant)
                
                with UnitOfWork(db) as inner:
                    user = User(
                        email="test@example.com",
                        password_hash="hash",
                        first_name="Test",
                        last_name="User",
                        tenant_id=1
                    )
                    db.session.add(user)
                    inner.commit()
                
                outer_committed = True
            
            assert outer_committed
            assert Tenant.query.count() == 1
            assert User.query.count() == 1
    
    def test_repository_registration(self, app):
        """Test repository registration and retrieval."""
        with app.app_context():
            from backend.shared.transaction import UnitOfWork
            
            with UnitOfWork(db) as uow:
                uow.register_repository('test', {'data': 'test'})
                
                repo = uow.get_repository('test')
                assert repo['data'] == 'test'
                
                with pytest.raises(KeyError):
                    uow.get_repository('nonexistent')
    
    def test_events_collected_on_commit(self, app):
        """Test that events are published only after commit."""
        with app.app_context():
            from backend.shared.transaction import UnitOfWork
            from dataclasses import dataclass
            
            @dataclass
            class TestEvent:
                name: str
            
            published_events = []
            
            with app.app_context():
                try:
                    from backend.shared.events.event_bus import EventBus
                    original_publish = EventBus.publish
                    
                    def mock_publish(self, event):
                        published_events.append(event)
                    
                    EventBus.publish = mock_publish
                    
                    with UnitOfWork(db) as uow:
                        tenant = Tenant(name="Test Tenant", slug="test")
                        db.session.add(tenant)
                        uow.add_event(TestEvent("created"))
                        uow.commit()
                finally:
                    from backend.shared.events.event_bus import EventBus
                    EventBus.publish = original_publish
            
            assert len(published_events) == 1
            assert published_events[0].name == "created"


class TestTransactionalDecorator:
    """Test cases for @transactional decorator."""
    
    @pytest.fixture
    def app(self):
        app = create_app(db_url="sqlite:///:memory:")
        app.config["TESTING"] = True
        with app.app_context():
            db.create_all()
            yield app
            db.session.remove()
            db.drop_all()
    
    def test_auto_commit_decorator(self, app):
        """Test @transactional with auto_commit=True."""
        with app.app_context():
            from backend.shared.transaction import transactional
            from backend.extensions import db
            
            class TestService:
                @transactional
                def create_tenant(self, name, slug):
                    tenant = Tenant(name=name, slug=slug)
                    db.session.add(tenant)
                    return tenant
            
            service = TestService()
            service.create_tenant("Test", "test")
            
            assert Tenant.query.count() == 1
    


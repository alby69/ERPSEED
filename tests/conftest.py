"""
Test fixtures and helpers for FlaskERP tests.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    os.environ['FLASK_ENV'] = 'testing'
    from backend import create_app
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    app.config['WTF_CSRF_ENABLED'] = False
    return app


@pytest.fixture(scope='function')
def db(app):
    """Create database for testing."""
    from backend.extensions import db as _db
    from backend.core.models import Tenant, AuditLog
    from backend.models import User, Product, SalesOrder
    from backend.entities.soggetto import Soggetto
    
    with app.app_context():
        # Create all tables
        _db.create_all()
        
        yield _db
        
        # Clean up after test
        try:
            _db.session.rollback()
            # Delete all data from all tables
            for table in reversed(_db.metadata.sorted_tables):
                _db.session.execute(table.delete())
            _db.session.commit()
        except Exception as e:
            _db.session.rollback()
            print(f"Cleanup error: {e}")
        finally:
            _db.drop_all()


@pytest.fixture(scope='function')
def session(db, app):
    """Create database session for testing."""
    with app.app_context():
        yield db.session


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def tenant(db, session):
    """Create a test tenant."""
    from backend.core.models import Tenant
    
    tenant = Tenant(
        name='Test Company',
        slug='test-company',
        email='admin@test.com',
        is_active=True
    )
    session.add(tenant)
    session.commit()
    session.refresh(tenant)
    return tenant


@pytest.fixture
def tenant2(db, session):
    """Create a second test tenant for isolation testing."""
    from backend.core.models import Tenant
    
    tenant = Tenant(
        name='Second Company',
        slug='second-company',
        email='admin@second.com',
        is_active=True
    )
    session.add(tenant)
    session.commit()
    session.refresh(tenant)
    return tenant


@pytest.fixture
def admin_user(db, session, tenant):
    """Create an admin user."""
    from backend.models import User
    
    user = User(
        tenant_id=tenant.id,
        email='admin@test.com',
        first_name='Admin',
        last_name='User',
        role='admin',
        is_primary=True
    )
    user.set_password('admin123')
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def regular_user(db, session, tenant):
    """Create a regular user."""
    from backend.models import User
    
    user = User(
        tenant_id=tenant.id,
        email='user@test.com',
        first_name='Regular',
        last_name='User',
        role='user'
    )
    user.set_password('user123')
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def admin_user2(db, session, tenant2):
    """Create an admin user for second tenant."""
    from backend.models import User
    
    user = User(
        tenant_id=tenant2.id,
        email='admin@second.com',
        first_name='Admin2',
        last_name='User2',
        role='admin',
        is_primary=True
    )
    user.set_password('admin123')
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def party(db, session, tenant):
    """Create a test party."""
    from backend.entities.soggetto import Soggetto
    
    party = Soggetto(
        tenant_id=tenant.id,
        nome='Test Customer',
        tipo_soggetto='persona_fisica',
        email_principale='customer@test.com',
        partita_iva='IT12345678901'
    )
    session.add(party)
    session.commit()
    session.refresh(party)
    return party


@pytest.fixture
def party2(db, session, tenant2):
    """Create a test party for tenant2."""
    from backend.entities.soggetto import Soggetto
    
    party = Soggetto(
        tenant_id=tenant2.id,
        nome='Customer Two',
        tipo_soggetto='persona_fisica',
        email_principale='customer@second.com',
        partita_iva='IT98765432109'
    )
    session.add(party)
    session.commit()
    session.refresh(party)
    return party


@pytest.fixture
def product(db, session, tenant):
    """Create a test product."""
    from backend.models import Product
    
    product = Product(
        tenant_id=tenant.id,
        name='Test Product',
        code='PROD001',
        unit_price=100.00
    )
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@pytest.fixture
def product2(db, session, tenant2):
    """Create a test product for tenant2."""
    from backend.models import Product
    
    product = Product(
        tenant_id=tenant2.id,
        name='Product Two',
        code='PROD002',
        unit_price=200.00
    )
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@pytest.fixture
def auth_headers(client, admin_user):
    """Get authentication headers for admin user."""
    response = client.post('/login', json={
        'email': 'admin@test.com',
        'password': 'admin123'
    })
    if response.status_code == 200:
        token = response.json.get('access_token')
        if token:
            return {'Authorization': f'Bearer {token}'}
    return {}


@pytest.fixture
def user_auth_headers(client, regular_user):
    """Get authentication headers for regular user."""
    response = client.post('/login', json={
        'email': 'user@test.com',
        'password': 'user123'
    })
    if response.status_code == 200:
        token = response.json.get('access_token')
        if token:
            return {'Authorization': f'Bearer {token}'}
    return {}

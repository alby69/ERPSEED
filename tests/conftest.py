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
    
    with app.app_context():
        _db.create_all()
        yield _db
        try:
            _db.session.rollback()
            for table in reversed(_db.metadata.sorted_tables):
                _db.session.execute(table.delete())
            _db.session.commit()
        except:
            _db.session.rollback()
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
def admin_user(db, session):
    """Create an admin user."""
    from backend.models import User
    
    user = User(
        email='admin@test.com',
        first_name='Admin',
        last_name='User',
        role='admin'
    )
    user.set_password('admin123')
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def regular_user(db, session):
    """Create a regular user."""
    from backend.models import User
    
    user = User(
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
def project(db, session, admin_user):
    """Create a test project."""
    from backend.models import Project
    
    project = Project(
        name='test_project',
        title='Test Project',
        description='A test project',
        owner_id=admin_user.id
    )
    project.members.append(admin_user)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@pytest.fixture
def sys_model(db, session, project):
    """Create a test SysModel."""
    from backend.models import SysModel
    
    model = SysModel(
        name='customers',
        title='Customers',
        description='Customer records',
        project_id=project.id
    )
    session.add(model)
    session.commit()
    session.refresh(model)
    return model


@pytest.fixture
def sys_field(db, session, sys_model):
    """Create a test SysField."""
    from backend.models import SysField
    
    field = SysField(
        name='name',
        title='Name',
        type='string',
        required=True,
        model_id=sys_model.id
    )
    session.add(field)
    session.commit()
    session.refresh(field)
    return field


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

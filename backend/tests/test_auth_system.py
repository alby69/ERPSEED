import pytest
import os
from backend import create_app
from backend.extensions import db
from backend.models import User
from backend.core.models import Tenant
from backend.core.services import AuthService

@pytest.fixture
def app():
    os.environ["JWT_SECRET_KEY"] = "test-secret-key-very-long-and-secure-enough"
    app = create_app("sqlite:///:memory:")
    app.config.update({
        "TESTING": True,
        "JWT_SECRET_KEY": "test-secret-key-very-long-and-secure-enough",
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_registration_and_login(client, app):
    # 1. Test Registration
    reg_data = {
        "email": "admin@test.com",
        "password": "Password123!",
        "first_name": "Test",
        "last_name": "User",
        "tenant_name": "Test Tenant",
        "tenant_slug": "test-tenant"
    }

    response = client.post("/api/v1/auth/register", json=reg_data)
    assert response.status_code == 201
    data = response.get_json()
    assert "access_token" in data
    assert "user" in data
    assert data["user"]["email"] == "admin@test.com"

    # Verify database
    with app.app_context():
        user = User.query.filter_by(email="admin@test.com").first()
        assert user is not None
        tenant = Tenant.query.filter_by(slug="test-tenant").first()
        assert tenant is not None

    # 2. Test Login
    login_data = {
        "email": "admin@test.com",
        "password": "Password123!"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_login_invalid_password(client, app):
    # Setup user
    with app.app_context():
        AuthService.register(
            email="bad@test.com",
            password="Correct123!",
            first_name="Bad",
            last_name="Login",
            tenant_name="Bad Tenant",
            tenant_slug="bad-tenant"
        )

    login_data = {
        "email": "bad@test.com",
        "password": "WrongPassword!"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401

def test_me_endpoint(client, app):
    # Register and get token
    reg_data = {
        "email": "me@test.com",
        "password": "Password123!",
        "first_name": "Me",
        "last_name": "User",
        "tenant_name": "Me Tenant",
        "tenant_slug": "me-tenant"
    }
    resp = client.post("/api/v1/auth/register", json=reg_data)
    token = resp.get_json()["access_token"]

    # Test /me
    response = client.get("/api/v1/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["email"] == "me@test.com"

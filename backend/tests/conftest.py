"""Shared fixtures for backend tests.

Configures Flask app with in-memory SQLite, registers auth user,
and initializes DI container services for CQRS-based modules.
"""
import pytest
import os
from backend import create_app
from backend.extensions import db
from backend.core.container import get_container


def _register_module_services():
    """Register all CQRS module services in the DI container."""
    container = get_container()
    from backend.modules.tax.container import register_tax_service
    from backend.modules.invoicing.container import register_invoicing_service
    register_tax_service(container)
    register_invoicing_service(container)


@pytest.fixture
def app():
    os.environ["JWT_SECRET_KEY"] = "test-secret-key-very-long-and-secure-enough"
    app = create_app("sqlite:///:memory:")
    app.config.update({
        "TESTING": True,
        "JWT_SECRET_KEY": "test-secret-key-very-long-and-secure-enough",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "CACHE_TYPE": "NullCache",
    })

    with app.app_context():
        db.create_all()
        _register_module_services()
        yield app
        db.session.remove()
        db.drop_all()
    from backend.plugins.registry import ModuleRegistry
    ModuleRegistry._plugins = {}
    ModuleRegistry._enabled_plugins = []
    from backend.extensions import cache
    cache.clear()
    # Clear cache after each test to prevent interference


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    reg_data = {
        "email": "admin@test.com",
        "password": "Password123!",
        "first_name": "Test",
        "last_name": "User",
        "tenant_name": "Test Tenant",
        "tenant_slug": "test-tenant"
    }
    resp = client.post("/api/v1/auth/register", json=reg_data)
    assert resp.status_code == 201
    data = resp.get_json()
    token = data["access_token"]
    return {"Authorization": f"Bearer {token}", "X-Tenant-ID": "1"}

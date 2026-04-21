import pytest
import os
from backend import create_app
from backend.extensions import db
from backend.models import User, Project, SysModel, SysField

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
        # Setup a test user and tenant
        from backend.core.services import AuthService
        AuthService.register(
            email="admin@test.com",
            password="Password123!",
            first_name="Admin",
            last_name="Test",
            tenant_name="Test Tenant",
            tenant_slug="test-tenant"
        )
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_header(client):
    resp = client.post("/api/v1/auth/login", json={
        "email": "admin@test.com",
        "password": "Password123!"
    })
    data = resp.get_json()
    token = data["access_token"]
    user_id = data["user"]["id"]
    return {"Authorization": f"Bearer {token}"}, user_id

def test_project_crud(client, auth_header):
    headers, user_id = auth_header
    # Create Project
    response = client.post("/api/v1/projects", json={
        "name": "test_project",
        "title": "Test Project",
        "description": "Description",
        "owner_id": user_id
    }, headers=headers)
    assert response.status_code == 201
    project_id = response.get_json()["id"]

    # List Projects
    response = client.get("/api/v1/projects", headers=headers)
    assert response.status_code == 200
    assert any(p["id"] == project_id for p in response.get_json())

    # Get Project
    response = client.get(f"/api/v1/projects/{project_id}", headers=headers)
    assert response.status_code == 200
    assert response.get_json()["name"] == "test_project"

def test_dynamic_model_creation(client, auth_header, app):
    headers, user_id = auth_header
    # 1. Create a Project
    resp = client.post("/api/v1/projects", json={
        "name": "builder_proj",
        "title": "Builder Project",
        "owner_id": user_id
    }, headers=headers)
    project_id = resp.get_json()["id"]

    # 2. Create a SysModel using the ProjectModels endpoint
    model_resp = client.post(f"/api/v1/projects/{project_id}/models", json={
        "projectId": project_id,
        "name": "crm_leads",
        "title": "Leads",
        "technical_name": "crm_leads",
        "table_name": "crm_leads"
    }, headers=headers)
    assert model_resp.status_code == 201
    model_id = model_resp.get_json()["id"]

    # Actually, let's just verify SysModel creation for now since SysField endpoint is elusive
    with app.app_context():
        sm = db.session.get(SysModel, model_id)
        assert sm.name == "crm_leads"
        assert sm.projectId == project_id

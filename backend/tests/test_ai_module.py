import pytest
import os
from unittest.mock import MagicMock, patch
from backend import create_app
from backend.extensions import db
from backend.modules.ai.application.commands.ai_commands import GenerateConfigCommand
from backend.modules.ai.application.handlers import AICommandHandler

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

def test_ai_handler_logic(app, auth_header):
    headers, user_id = auth_header

    # Mocking the AI Service adapter (internal method)
    with patch('backend.modules.ai.service.AIService.generate_erp_config') as mock_generate:
        mock_generate.return_value = {"models": [{"name": "test_model", "fields": []}]}

        handler = AICommandHandler()
        cmd = GenerateConfigCommand(
            projectId=1,
            userId=user_id,
            user_request="Create a CRM",
        )

        result = handler.handle_generate_config(cmd)
        assert "models" in result
        assert result["models"][0]["name"] == "test_model"

def test_ai_models_api(client, auth_header):
    headers, user_id = auth_header

    response = client.get("/api/v1/ai/models", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert "models" in data
    assert isinstance(data["models"], list)

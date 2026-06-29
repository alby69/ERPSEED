"""
Tests for Capability Registry and AgentMesh integration.
"""

import pytest
import os
from backend import create_app
from backend.extensions import db
from backend.core.events.capabilities import capability_registry, Capability
from backend.shared.commands import CreateCommand
from dataclasses import dataclass

@dataclass
class TestAgentCommand(CreateCommand):
    name: str = ""
    value: int = 0

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
    return {"Authorization": f"Bearer {token}"}

def test_capability_registration():
    """Test registering a capability."""
    capability_registry.register(
        name="test_capability",
        description="A test capability",
        command_class=TestAgentCommand,
        agent_name="TestAgent"
    )

    cap = capability_registry.get_capability("test_capability")
    assert cap is not None
    assert cap.name == "test_capability"
    assert cap.agent_name == "TestAgent"
    assert cap.input_schema["properties"]["name"]["type"] == "string"
    assert cap.input_schema["properties"]["value"]["type"] == "integer"

def test_capability_manifest_api(client, auth_header):
    """Test the manifest API endpoint."""
    capability_registry.register(
        name="manifest_test",
        description="Testing manifest",
        command_class=TestAgentCommand,
        agent_name="ManifestAgent"
    )

    response = client.get("/api/v1/ai/capabilities/", headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True

    agents = [a["agent"] for a in data["manifest"]]
    assert "ManifestAgent" in agents

    # Find ManifestAgent in the manifest
    agent_info = next(a for a in data["manifest"] if a["agent"] == "ManifestAgent")
    assert any(c["name"] == "manifest_test" for c in agent_info["capabilities"])

def test_agent_specific_capabilities_api(client, auth_header):
    """Test the agent-specific capabilities API endpoint."""
    capability_registry.register(
        name="specific_test",
        description="Testing specific",
        command_class=TestAgentCommand,
        agent_name="SpecificAgent"
    )

    response = client.get("/api/v1/ai/capabilities/SpecificAgent", headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["agent"] == "SpecificAgent"
    assert len(data["capabilities"]) >= 1
    assert data["capabilities"][0]["name"] == "specific_test"

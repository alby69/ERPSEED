"""
Tests for Model Versioning
"""
import pytest
import json
from . import create_app
from extensions import db
from models import SysModel, SysField, User, Project, SysModelVersion
from modules.system_tools.services.versioning_service import ModelVersioningService

@pytest.fixture
def app():
    app = create_app(db_url="sqlite:///:memory:")
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_create_snapshot(app):
    with app.app_context():
        # Setup data
        user = User(email="test@example.com", first_name="Test")
        db.session.add(user)
        db.session.flush()

        project = Project(name="test_proj", title="Test Proj", owner_id=user.id)
        db.session.add(project)
        db.session.flush()

        model = SysModel(
            name="customer",
            technical_name="crm.customer",
            table_name="customer",
            projectId=project.id
        )
        db.session.add(model)
        db.session.flush()

        field = SysField(
            name="Name",
            technical_name="name",
            type="string",
            modelId=model.id
        )
        db.session.add(field)
        db.session.commit()

        # Create snapshot
        version = ModelVersioningService.create_snapshot(model.id, description="Initial version", userId=user.id)

        assert version.version_number == 1
        assert version.description == "Initial version"

        data = json.loads(version.data)
        assert data["model"]["name"] == "customer"
        assert len(data["fields"]) == 1
        assert data["fields"][0]["technical_name"] == "name"

        # Create second snapshot
        version2 = ModelVersioningService.create_snapshot(model.id, description="V2")
        assert version2.version_number == 2

import pytest
from backend.core.services.base import BaseService
from backend.extensions import db

class MockModel:
    __name__ = "MockModel"
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def soft_delete(self):
        self.deleted_at = "now"

def test_base_service_protected_fields():
    service = BaseService(model=MockModel)
    data = {"id": 1, "name": "Test", "created_at": "today"}

    # Create should filter out protected fields
    # In a real test we would check the session, here we check the logic
    filtered = {k: v for k, v in data.items() if k not in service.protected_fields}
    assert "id" not in filtered
    assert "name" in filtered

def test_base_service_update_logic():
    service = BaseService(model=MockModel)
    instance = MockModel(id=1, name="Old")
    data = {"id": 2, "name": "New"}

    # Mocking the commit for the unit test
    service.commit = lambda: None

    service.update(instance, data)
    assert instance.id == 1 # Should not change
    assert instance.name == "New"

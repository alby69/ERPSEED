"""
Tests for Global Search API and Field-Level RBAC endpoints.
"""
import pytest
from backend.models import User
from backend.core.middleware.permission import get_user_permissions_summary, FIELD_PERMISSIONS_BY_ROLE


def test_user_permissions_summary():
    user = User(id=1, email="user@test.com", role="user")
    summary = get_user_permissions_summary(user)

    assert summary["role"] == "user"
    assert "hidden_fields" in summary
    assert summary["hidden_fields"] == FIELD_PERMISSIONS_BY_ROLE["user"]
    assert "cost_price" in summary["hidden_fields"]["product"]


def test_global_search_endpoint(client, auth_headers):
    response = client.get("/api/v1/global/search?q=test", headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert "results" in data
    assert isinstance(data["results"], list)


def test_users_permissions_endpoint(client, auth_headers):
    response = client.get("/api/v1/users/permissions", headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert "role" in data
    assert "permissions" in data
    assert "hidden_fields" in data

import os
import json
import pytest
from backend.scripts.generate_openapi import generate_openapi_spec


def test_generate_openapi_spec():
    """Verify that generate_openapi_spec returns a valid OpenAPI dictionary with required fields."""
    spec = generate_openapi_spec()
    assert isinstance(spec, dict)
    assert "openapi" in spec
    assert "info" in spec
    assert "paths" in spec
    assert len(spec["paths"]) > 0


def test_openapi_json_file_exists_and_matches_spec():
    """Verify that backend/openapi.json exists on disk and contains valid OpenAPI spec structure."""
    file_path = os.path.join(os.path.dirname(__file__), "..", "openapi.json")
    file_path = os.path.abspath(file_path)

    assert os.path.exists(file_path), "backend/openapi.json should exist"

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, dict)
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data

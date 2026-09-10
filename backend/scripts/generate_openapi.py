#!/usr/bin/env python3
"""
OpenAPI Specification Generator
--------------------------------
Generates `backend/openapi.json` from the Flask application's OpenAPI specification.
Used by CI/CD workflows and local development to keep API specs up to date for AgentMesh integration.
"""

import os
import sys
import json

# Ensure project root is in PYTHONPATH
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Set fallback JWT_SECRET_KEY for initialization if missing
if not os.getenv("JWT_SECRET_KEY"):
    os.environ["JWT_SECRET_KEY"] = "openapi-spec-generator-secret-key-min-32-chars"

from backend import create_app, api


def generate_openapi_spec(output_path=None):
    if output_path is None:
        output_path = os.path.join(PROJECT_ROOT, "backend", "openapi.json")

    app = create_app()
    with app.app_context():
        spec_dict = api.spec.to_dict()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(spec_dict, f, indent=2, ensure_ascii=False)

    print(f"OpenAPI spec generated successfully at: {output_path}")
    return spec_dict


if __name__ == "__main__":
    generate_openapi_spec()

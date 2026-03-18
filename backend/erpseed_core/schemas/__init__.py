"""
JSON Schemas Module

Provides validation against JSON schemas for:
- model
- block
- module
- workflow
- business_rule
- project
"""

import json
import jsonschema
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional


SCHEMAS_DIR = Path(__file__).parent / "schemas"


def load_schema(schema_name: str) -> Dict[str, Any]:
    """Load a JSON schema by name"""
    schema_path = SCHEMAS_DIR / f"{schema_name}_schema.json"
    if not schema_path.exists():
        return {}
    return json.loads(schema_path.read_text())


def validate_against_schema(data: Dict[str, Any], schema_name: str) -> Tuple[bool, List[str]]:
    """Validate data against a schema"""
    schema = load_schema(schema_name)
    if not schema:
        return False, [f"Schema '{schema_name}' not found"]
    
    validator = jsonschema.Draft7Validator(schema)
    errors = list(validator.iter_errors(data))
    
    if not errors:
        return True, []
    
    error_messages = [f"{e.json_path}: {e.message}" for e in errors]
    return False, error_messages


def validate_model(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate a model definition"""
    return validate_against_schema(data, "model")


def validate_block(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate a block definition"""
    return validate_against_schema(data, "block")


def validate_module(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate a module definition"""
    return validate_against_schema(data, "module")


def validate_workflow(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate a workflow definition"""
    return validate_against_schema(data, "workflow")


def validate_business_rule(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate a business rule definition"""
    return validate_against_schema(data, "business_rule")


def validate_project(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate a project definition"""
    return validate_against_schema(data, "project")

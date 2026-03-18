"""
Parser Module - Parse Python spec files to JSON

This module provides functionality to parse Python-based specification
files and convert them to JSON format for ERPSEED Core.
"""

import ast
import json
from pathlib import Path
from typing import Any, Dict, Union


def parse_spec_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Parse a Python spec file and convert to JSON"""
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Spec file not found: {file_path}")
    
    content = path.read_text()
    
    tree = ast.parse(content)
    
    result = {
        "name": path.stem,
        "version": "1.0.0",
        "models": [],
        "blocks": [],
        "workflows": [],
        "business_rules": [],
    }
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_data = _parse_class(node)
            if class_data:
                entity_type = class_data.get("type", "model")
                if entity_type == "model":
                    result["models"].append(class_data)
                elif entity_type == "block":
                    result["blocks"].append(class_data)
                elif entity_type == "workflow":
                    result["workflows"].append(class_data)
                elif entity_type == "business_rule":
                    result["business_rules"].append(class_data)
    
    return result


def _parse_class(node: ast.ClassDef) -> Dict[str, Any]:
    """Parse a class definition"""
    class_data = {
        "name": node.name,
        "technical_name": _to_snake_case(node.name),
        "type": "model",
    }
    
    for base in node.bases:
        if isinstance(base, ast.Name):
            base_name = base.id.lower()
            if base_name in ["model", "block", "workflow", "businessrule", "business_rule"]:
                class_data["type"] = "model" if base_name == "model" else base_name
    
    for item in node.body:
        if isinstance(item, ast.AnnAssign):
            if isinstance(item.target, ast.Name):
                field_name = item.target.id
                
                if field_name == "__type__":
                    class_data["type"] = _extract_value(item.value)
                elif field_name == "__model__":
                    class_data["model"] = _extract_value(item.value)
                elif field_name.startswith("__"):
                    continue
                else:
                    field = _parse_field(item)
                    class_data.setdefault("fields", []).append(field)
        
        elif isinstance(item, ast.FunctionDef):
            method_data = _parse_method(item)
            if method_data:
                class_data.setdefault("methods", []).append(method_data)
    
    return class_data


def _parse_field(ann_assign: ast.AnnAssign) -> Dict[str, Any]:
    """Parse a field annotation"""
    field = {
        "name": ann_assign.target.id,
        "type": "string",
    }
    
    if isinstance(ann_assign.annotation, ast.Name):
        type_map = {
            "str": "string",
            "int": "integer",
            "float": "float",
            "bool": "boolean",
            "date": "date",
            "datetime": "datetime",
        }
        field["type"] = type_map.get(ann_assign.annotation.id, "string")
    
    if ann_assign.value:
        field["default"] = _extract_value(ann_assign.value)
    
    return field


def _parse_method(func: ast.FunctionDef) -> Dict[str, Any]:
    """Parse a method definition"""
    method = {
        "name": func.name,
        "args": [arg.arg for arg in func.args.args],
    }
    
    docstring = ast.get_docstring(func)
    if docstring:
        method["doc"] = docstring
    
    return method


def _extract_value(value: ast.AST) -> Any:
    """Extract value from an AST node"""
    if isinstance(value, ast.Constant):
        return value.value
    elif isinstance(value, ast.Str):
        return value.s
    elif isinstance(value, ast.Num):
        return value.n
    elif isinstance(value, ast.NameConstant):
        return value.value
    elif isinstance(value, ast.List):
        return [_extract_value(el) for el in value.elts]
    elif isinstance(value, ast.Dict):
        result = {}
        for key, val in zip(value.keys, value.values):
            k = _extract_value(key)
            v = _extract_value(val)
            result[k] = v
        return result
    return None


def _to_snake_case(name: str) -> str:
    """Convert CamelCase to snake_case"""
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

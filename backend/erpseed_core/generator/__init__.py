"""
Generator Module - Export project to JSON

This module provides functionality to export ERPSEED projects
to JSON format.
"""

import json
from pathlib import Path
from typing import Any, Dict, Union


def export_project(project_path: Union[str, Path]) -> Dict[str, Any]:
    """Export entire project to JSON"""
    path = Path(project_path)
    
    project_file = path / "project.json"
    if not project_file.exists():
        raise FileNotFoundError(f"project.json not found in {project_path}")
    
    result = json.loads(project_file.read_text())
    
    models_dir = path / "models"
    if models_dir.exists():
        result["models"] = []
        for model_file in models_dir.glob("*.json"):
            model_data = json.loads(model_file.read_text())
            result["models"].append(model_data)
    
    blocks_dir = path / "blocks"
    if blocks_dir.exists():
        result["blocks"] = []
        for block_file in blocks_dir.glob("*.json"):
            block_data = json.loads(block_file.read_text())
            result["blocks"].append(block_data)
    
    workflows_dir = path / "workflows"
    if workflows_dir.exists():
        result["workflows"] = []
        for wf_file in workflows_dir.glob("*.json"):
            wf_data = json.loads(wf_file.read_text())
            result["workflows"].append(wf_data)
    
    br_dir = path / "business_rules"
    if br_dir.exists():
        result["business_rules"] = []
        for br_file in br_dir.glob("*.json"):
            br_data = json.loads(br_file.read_text())
            result["business_rules"].append(br_data)
    
    return result


def export_model(model_data: Dict[str, Any]) -> str:
    """Export a single model to JSON string"""
    return json.dumps(model_data, indent=2)


def export_block(block_data: Dict[str, Any]) -> str:
    """Export a single block to JSON string"""
    return json.dumps(block_data, indent=2)


def export_workflow(workflow_data: Dict[str, Any]) -> str:
    """Export a single workflow to JSON string"""
    return json.dumps(workflow_data, indent=2)


def export_business_rule(rule_data: Dict[str, Any]) -> str:
    """Export a single business rule to JSON string"""
    return json.dumps(rule_data, indent=2)


def save_model(model_data: Dict[str, Any], output_dir: Union[str, Path]) -> Path:
    """Save model JSON to file"""
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    
    technical_name = model_data.get("technical_name", "model")
    output_file = path / f"{technical_name}.json"
    
    output_file.write_text(json.dumps(model_data, indent=2))
    return output_file


def save_block(block_data: Dict[str, Any], output_dir: Union[str, Path]) -> Path:
    """Save block JSON to file"""
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    
    technical_name = block_data.get("technical_name", "block")
    output_file = path / f"{technical_name}.json"
    
    output_file.write_text(json.dumps(block_data, indent=2))
    return output_file


def save_workflow(workflow_data: Dict[str, Any], output_dir: Union[str, Path]) -> Path:
    """Save workflow JSON to file"""
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    
    technical_name = workflow_data.get("technical_name", "workflow")
    output_file = path / f"{technical_name}.json"
    
    output_file.write_text(json.dumps(workflow_data, indent=2))
    return output_file


def save_business_rule(rule_data: Dict[str, Any], output_dir: Union[str, Path]) -> Path:
    """Save business rule JSON to file"""
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    
    technical_name = rule_data.get("technical_name", "rule")
    output_file = path / f"{technical_name}.json"
    
    output_file.write_text(json.dumps(rule_data, indent=2))
    return output_file

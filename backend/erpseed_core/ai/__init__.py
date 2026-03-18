"""
AI Integration Module - DeepSeek integration for natural language generation

This module provides AI-powered generation of ERPSEED components
using the DeepSeek API.
"""

import os
import json
from typing import Any, Dict, Optional


class AIClient:
    """DeepSeek AI client for generating ERP components"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.deepseek.com"):
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        self.base_url = base_url
    
    def generate_model(self, description: str) -> Dict[str, Any]:
        """Generate a data model from natural language description"""
        prompt = f"""Generate a JSON model definition for an ERPSEED ERP system based on this description: {description}

Return a JSON object with these fields:
- name: display name
- technical_name: snake_case identifier
- table_name: database table name
- title: human-readable title
- description: description
- fields: array of field objects with:
  - name: field name (snake_case)
  - type: field type (string, integer, float, boolean, date, datetime, many2one, many2many, one2many, selection)
  - title: field title
  - required: boolean
  - unique: boolean
  - widget: widget type

Return ONLY valid JSON, no explanation."""
        
        return self._call_api(prompt)
    
    def generate_block(self, description: str, model: str) -> Dict[str, Any]:
        """Generate a UI block from natural language description"""
        prompt = f"""Generate a JSON block definition for an ERPSEED ERP system based on this description: {description}

The block should use model: {model}

Return a JSON object with these fields:
- name: display name
- technical_name: snake_case identifier  
- type: block type (form, list, tree, kanban, calendar, graph)
- title: human-readable title
- model: associated model technical name
- fields: array of block field objects with:
  - model_field: name of the model field
  - widget: widget type
  - order: display order
  - col_span: column span (1-12)
  - label: field label
  - visible: boolean
  - editable: boolean

Return ONLY valid JSON, no explanation."""
        
        return self._call_api(prompt)
    
    def generate_workflow(self, description: str, model: str) -> Dict[str, Any]:
        """Generate a workflow from natural language description"""
        prompt = f"""Generate a JSON workflow definition for an ERPSEED ERP system based on this description: {description}

The workflow should apply to model: {model}

Return a JSON object with these fields:
- name: display name
- technical_name: snake_case identifier
- model: associated model technical name
- title: human-readable title
- description: description
- states: array of state objects with:
  - name: state name
  - type: state type (active, done, cancelled)
  - permissions: array of permission strings
- initial_state: name of initial state
- transitions: array of transition objects with:
  - from_state: source state
  - to_state: destination state
  - action: action name
  - trigger: trigger type (manual, on_create, on_save)

Return ONLY valid JSON, no explanation."""
        
        return self._call_api(prompt)
    
    def generate_business_rule(self, description: str, model: str) -> Dict[str, Any]:
        """Generate a business rule from natural language description"""
        prompt = f"""Generate a JSON business rule definition for an ERPSEED ERP system based on this description: {description}

The rule should apply to model: {model}

Return a JSON object with these fields:
- name: display name
- technical_name: snake_case identifier
- model: associated model technical name
- type: rule type (validation, computation, action, constraint)
- title: human-readable title
- description: description
- conditions: array of condition objects with:
  - field: field name
  - operator: operator (==, !=, >, <, >=, <=, in, not_in, like, is_null)
  - value: comparison value
- actions: array of action objects with:
  - type: action type
  - params: action parameters
- trigger: trigger type (on_save, on_create, on_delete, manual)
- priority: integer priority
- enabled: boolean

Return ONLY valid JSON, no explanation."""
        
        return self._call_api(prompt)
    
    def generate_project(self, description: str) -> Dict[str, Any]:
        """Generate a complete project from natural language description"""
        prompt = f"""Generate a complete JSON project definition for an ERPSEED ERP system based on this description: {description}

Return a JSON object with:
- name: project name
- version: version string (1.0.0)
- description: project description
- models: array of model definitions
- blocks: array of block definitions
- workflows: array of workflow definitions
- business_rules: array of business rule definitions
- settings: settings object with database config

Generate at least 2-3 related models with fields, 2-3 blocks, 1 workflow, and 1 business rule that make sense together.

Return ONLY valid JSON, no explanation."""
        
        return self._call_api(prompt)
    
    def _call_api(self, prompt: str) -> Dict[str, Any]:
        """Make API call to DeepSeek"""
        if not self.api_key:
            raise ValueError("DeepSeek API key not configured")
        
        try:
            import requests
            
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7
                },
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            content = result["choices"][0]["message"]["content"]
            
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            return json.loads(content.strip())
            
        except ImportError:
            raise ImportError("requests library required for AI integration")
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response as JSON: {e}")
        except Exception as e:
            raise RuntimeError(f"AI API call failed: {e}")


def get_client() -> AIClient:
    """Get configured AI client"""
    return AIClient()

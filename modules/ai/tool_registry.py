"""
Tool Registry - Core per la gestione dei tool dinamici
Implementa conversione SysModel -> tool definitions (Anthropic/OpenAI)
"""

import json
import logging
from typing import Dict, List, Any, Optional, Callable
from functools import lru_cache
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Registry centrale per la gestione dei tool dinamici.
    Converte i modelli FlaskERP in definizioni tool per LLM.
    """

    TYPE_MAPPING = {
        "string": "string",
        "text": "string",
        "integer": "integer",
        "decimal": "number",
        "float": "number",
        "currency": "number",
        "boolean": "boolean",
        "date": "string",
        "datetime": "string",
        "select": "string",
        "relation": "integer",
        "file": "string",
        "image": "string",
        "json": "object",
        "tags": "array",
        "lookup": "string",
        "summary": "number",
        "formula": "number",
        "calculated": "number",
    }

    EXCLUDED_FIELD_TYPES = {"formula", "summary", "calculated", "lines"}

    def __init__(self):
        self._tool_handlers: Dict[str, Callable] = {}
        self._cache_ttl = 300  # 5 minuti default
        self._tools_cache: Dict[str, tuple] = {}

    def register_handler(self, tool_name: str, handler: Callable):
        """Registra un handler per un tool specifico."""
        self._tool_handlers[tool_name] = handler
        logger.info(f"Registered tool handler: {tool_name}")

    def execute_tool(self, tool_name: str, arguments: Dict, context: Dict) -> Any:
        """Esegue un tool registrato."""
        if tool_name not in self._tool_handlers:
            raise ValueError(f"Tool not found: {tool_name}")

        handler = self._tool_handlers[tool_name]
        return handler(arguments, context)

    def field_to_json_schema(self, field) -> Dict:
        """Converte un SysField in JSON Schema."""
        schema = {"type": self.TYPE_MAPPING.get(field.type, "string")}

        if field.title:
            schema["description"] = field.title

        if field.type == "select" and field.options:
            try:
                opts = json.loads(field.options)
                if isinstance(opts, list):
                    enum_values = []
                    for o in opts:
                        if isinstance(o, dict):
                            enum_values.append(o.get("value", o.get("label")))
                        else:
                            enum_values.append(o)
                    schema["enum"] = enum_values
            except (json.JSONDecodeError, AttributeError):
                pass

        if field.type == "relation" and field.options:
            try:
                opts = json.loads(field.options)
                target = opts.get("target_table", "unknown")
                schema["description"] = f"ID of related {target} record"
            except json.JSONDecodeError:
                pass

        if field.type == "tags":
            schema["items"] = {"type": "string"}

        if field.type in ("date", "datetime"):
            schema["format"] = field.type

        if field.validation_regex and field.type in ("string", "text"):
            schema["pattern"] = field.validation_regex

        if field.default_value:
            try:
                if field.type == "boolean":
                    schema["default"] = field.default_value.lower() in ("true", "1")
                elif field.type in ("integer", "decimal", "float", "currency"):
                    schema["default"] = float(field.default_value)
                else:
                    schema["default"] = field.default_value
            except (ValueError, TypeError):
                pass

        return schema

    def model_to_tool(self, sys_model, operations: List[str] = None) -> List[Dict]:
        """
        Converte un SysModel in una lista di tool definitions.

        Args:
            sys_model: Istanza SysModel
            operations: Lista operazioni da generare ['list', 'create', 'get', 'update', 'delete']

        Returns:
            Lista di definizioni tool
        """
        if operations is None:
            operations = ["list", "create", "get", "update", "delete"]

        tools = []
        model_name = sys_model.name

        # Tool: list_<model>
        if "list" in operations:
            tools.append(self._generate_list_tool(model_name, sys_model))

        # Tool: create_<model>
        if "create" in operations:
            tools.append(self._generate_create_tool(model_name, sys_model))

        # Tool: get_<model>
        if "get" in operations:
            tools.append(self._generate_get_tool(model_name, sys_model))

        # Tool: update_<model>
        if "update" in operations:
            tools.append(self._generate_update_tool(model_name, sys_model))

        # Tool: delete_<model>
        if "delete" in operations:
            tools.append(self._generate_delete_tool(model_name, sys_model))

        return tools

    def _generate_list_tool(self, model_name: str, sys_model) -> Dict:
        """Genera tool per listare record."""
        properties = {
            "page": {"type": "integer", "default": 1, "description": "Page number"},
            "per_page": {
                "type": "integer",
                "default": 10,
                "description": "Items per page",
            },
            "q": {"type": "string", "description": "Search query"},
            "sort_by": {"type": "string", "description": "Field to sort by"},
            "sort_order": {
                "type": "string",
                "enum": ["asc", "desc"],
                "default": "desc",
            },
        }

        return {
            "name": f"list_{model_name}",
            "description": f"List records from {sys_model.title or model_name} model. Supports filtering, pagination, sorting.",
            "input_schema": {
                "type": "object",
                "properties": properties,
            },
        }

    def _generate_create_tool(self, model_name: str, sys_model) -> Dict:
        """Genera tool per creare record."""
        properties = {}
        required = []

        for field in sys_model.fields:
            if field.type in self.EXCLUDED_FIELD_TYPES:
                continue

            properties[field.name] = self.field_to_json_schema(field)

            if field.required:
                required.append(field.name)

        return {
            "name": f"create_{model_name}",
            "description": f"Create a new record in {sys_model.title or model_name} model.",
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }

    def _generate_get_tool(self, model_name: str, sys_model) -> Dict:
        """Genera tool per ottenere un record singolo."""
        return {
            "name": f"get_{model_name}",
            "description": f"Get a single record from {sys_model.title or model_name} by ID.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "ID of the record to retrieve",
                    }
                },
                "required": ["id"],
            },
        }

    def _generate_update_tool(self, model_name: str, sys_model) -> Dict:
        """Genera tool per aggiornare record."""
        properties = {
            "id": {"type": "integer", "description": "ID of the record to update"}
        }
        required = ["id"]

        for field in sys_model.fields:
            if field.type in self.EXCLUDED_FIELD_TYPES:
                continue
            if field.name == "id":
                continue

            properties[field.name] = self.field_to_json_schema(field)

        return {
            "name": f"update_{model_name}",
            "description": f"Update an existing record in {sys_model.title or model_name}.",
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }

    def _generate_delete_tool(self, model_name: str, sys_model) -> Dict:
        """Genera tool per eliminare record."""
        return {
            "name": f"delete_{model_name}",
            "description": f"Delete a record from {sys_model.title or model_name}.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "ID of the record to delete",
                    }
                },
                "required": ["id"],
            },
        }

    def to_anthropic_format(self, tools: List[Dict]) -> List[Dict]:
        """
        Converte tool definitions nel formato Anthropic.

        Formato Anthropic:
        {
            "name": "tool_name",
            "description": "...",
            "input_schema": {...}
        }
        """
        result = []
        for tool in tools:
            if "function" in tool:
                result.append(
                    {
                        "name": tool["function"]["name"],
                        "description": tool["function"].get("description", ""),
                        "input_schema": tool["function"].get(
                            "parameters", {"type": "object"}
                        ),
                    }
                )
            else:
                result.append(tool)

        return result

    def to_openai_format(self, tools: List[Dict]) -> List[Dict]:
        """
        Converte tool definitions nel formato OpenAI.

        Formato OpenAI:
        {
            "type": "function",
            "function": {
                "name": "...",
                "description": "...",
                "parameters": {...}
            }
        }
        """
        result = []
        for tool in tools:
            if "input_schema" in tool:
                result.append(
                    {
                        "type": "function",
                        "function": {
                            "name": tool["name"],
                            "description": tool.get("description", ""),
                            "parameters": tool["input_schema"],
                        },
                    }
                )
            else:
                result.append(tool)

        return result

    def get_tools_for_project(
        self,
        project_id: int,
        provider: str = "openrouter",
        operations: List[str] = None,
        use_cache: bool = True,
    ) -> List[Dict]:
        """
        Ottiene tutti i tool per un progetto.

        Args:
            project_id: ID del progetto
            provider: 'anthropic' o 'openrouter'
            operations: Operazioni da includere
            use_cache: Usa cache se disponibile

        Returns:
            Lista di tool definitions nel formato corretto
        """
        cache_key = f"{project_id}:{provider}:{operations}"

        if use_cache and cache_key in self._tools_cache:
            cached_data, cached_time = self._tools_cache[cache_key]
            if (datetime.now() - cached_time) < timedelta(seconds=self._cache_ttl):
                logger.debug(f"Returning cached tools for {cache_key}")
                return cached_data

        from models import SysModel

        models = SysModel.query.filter_by(
            project_id=project_id, status="published"
        ).all()

        all_tools = []
        for model in models:
            try:
                _ = model.fields
                tools = self.model_to_tool(model, operations)
                all_tools.extend(tools)
            except Exception as e:
                logger.warning(f"Error generating tools for model {model.name}: {e}")

        if provider == "anthropic":
            result = self.to_anthropic_format(all_tools)
        else:
            result = self.to_openai_format(all_tools)

        self._tools_cache[cache_key] = (result, datetime.now())

        return result

    def invalidate_cache(self, project_id: int = None):
        """Invalidate cache. Se project_id è None, invalida tutto."""
        if project_id:
            keys_to_remove = [
                k for k in self._tools_cache if k.startswith(f"{project_id}:")
            ]
            for key in keys_to_remove:
                del self._tools_cache[key]
        else:
            self._tools_cache.clear()

        logger.info(f"Cache invalidated for project_id={project_id}")

    def set_cache_ttl(self, seconds: int):
        """Imposta TTL per la cache."""
        self._cache_ttl = seconds

    def get_business_logic_tools(self, project_id: int = None) -> List[Dict]:
        """
        Genera tool per la business logic (workflow, hooks, scheduled tasks).

        Args:
            project_id: ID del progetto (opzionale)

        Returns:
            Lista di tool definitions per automazione
        """
        tools = []

        tools.extend(self._generate_workflow_tools())
        tools.extend(self._generate_hook_tools())
        tools.extend(self._generate_scheduled_task_tools())

        return tools

    def _generate_workflow_tools(self) -> List[Dict]:
        """Genera tool per workflow automation."""
        return [
            {
                "name": "create_workflow_automation",
                "description": "Create a complete workflow automation with trigger, conditions, and actions. Use this to automate business processes based on record events.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the workflow automation",
                        },
                        "trigger_model": {
                            "type": "string",
                            "description": "Model that triggers the workflow (e.g., 'ordini', 'clienti')",
                        },
                        "trigger_event": {
                            "type": "string",
                            "enum": [
                                "record.created",
                                "record.updated",
                                "record.deleted",
                            ],
                            "description": "Event that triggers the workflow",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional description",
                        },
                        "steps": {
                            "type": "array",
                            "description": "Array of workflow steps",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "step_type": {
                                        "type": "string",
                                        "enum": [
                                            "condition",
                                            "action",
                                            "notification",
                                            "delay",
                                            "webhook",
                                        ],
                                        "description": "Type of step",
                                    },
                                    "name": {
                                        "type": "string",
                                        "description": "Step name",
                                    },
                                    "config": {
                                        "type": "object",
                                        "description": "Step configuration",
                                    },
                                },
                                "required": ["step_type", "name", "config"],
                            },
                        },
                    },
                    "required": ["name", "trigger_event", "steps"],
                },
            },
            {
                "name": "update_workflow",
                "description": "Update an existing workflow automation",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "integer",
                            "description": "ID of the workflow to update",
                        },
                        "name": {
                            "type": "string",
                            "description": "New name (optional)",
                        },
                        "is_active": {
                            "type": "boolean",
                            "description": "Enable or disable workflow",
                        },
                        "steps": {
                            "type": "array",
                            "description": "New steps configuration",
                        },
                    },
                    "required": ["workflow_id"],
                },
            },
            {
                "name": "delete_workflow",
                "description": "Delete a workflow automation",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "integer",
                            "description": "ID of the workflow to delete",
                        }
                    },
                    "required": ["workflow_id"],
                },
            },
        ]

    def _generate_hook_tools(self) -> List[Dict]:
        """Genera tool per hooks e regole di business."""
        return [
            {
                "name": "register_business_rule",
                "description": "Register a business rule (hook) on a model to validate data or execute logic when records are created, updated, or deleted.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "model_name": {
                            "type": "string",
                            "description": "Name of the model to attach the rule to",
                        },
                        "hook_type": {
                            "type": "string",
                            "enum": [
                                "before_create",
                                "after_create",
                                "before_update",
                                "after_update",
                                "before_delete",
                                "after_delete",
                            ],
                            "description": "When the rule should trigger",
                        },
                        "rule_name": {
                            "type": "string",
                            "description": "Descriptive name for the rule",
                        },
                        "rule_logic": {
                            "type": "string",
                            "description": "Description or Python code for the rule logic",
                        },
                        "condition": {
                            "type": "object",
                            "description": "Optional condition that must be met for the rule to execute",
                            "properties": {
                                "field": {"type": "string"},
                                "operator": {"type": "string"},
                                "value": {"type": "string"},
                            },
                        },
                        "action": {
                            "type": "object",
                            "description": "Action to perform when rule triggers",
                            "properties": {
                                "type": {"type": "string"},
                                "config": {"type": "object"},
                            },
                        },
                    },
                    "required": ["model_name", "hook_type"],
                },
            },
            {
                "name": "list_business_rules",
                "description": "List all business rules (hooks) for a model or entire project",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "model_name": {
                            "type": "string",
                            "description": "Filter by model name (optional)",
                        }
                    },
                },
            },
            {
                "name": "delete_business_rule",
                "description": "Delete a business rule",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "model_name": {
                            "type": "string",
                            "description": "Model containing the rule",
                        },
                        "rule_id": {
                            "type": "integer",
                            "description": "ID of the rule to delete",
                        },
                    },
                    "required": ["model_name", "rule_id"],
                },
            },
        ]

    def _generate_scheduled_task_tools(self) -> List[Dict]:
        """Genera tool per task programmati."""
        return [
            {
                "name": "create_scheduled_task",
                "description": "Create a scheduled task that runs automatically at specified times (cron-like scheduling)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Task name"},
                        "description": {
                            "type": "string",
                            "description": "Task description",
                        },
                        "schedule": {
                            "type": "string",
                            "description": "Schedule in cron format or simple format (e.g., '5m' for every 5 minutes, '1h' for every hour, '1d' for daily)",
                        },
                        "task_type": {
                            "type": "string",
                            "enum": ["webhook", "email", "script"],
                            "description": "Type of task to execute",
                        },
                        "config": {
                            "type": "object",
                            "description": "Task-specific configuration",
                        },
                    },
                    "required": ["name", "schedule", "task_type"],
                },
            },
            {
                "name": "delete_scheduled_task",
                "description": "Delete a scheduled task",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "ID of the task to delete",
                        }
                    },
                    "required": ["task_id"],
                },
            },
            {
                "name": "setup_notification",
                "description": "Configure automatic notifications for specific events",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Notification name"},
                        "type": {
                            "type": "string",
                            "enum": ["email", "webhook", "log"],
                            "description": "Notification delivery method",
                        },
                        "target": {
                            "type": "string",
                            "description": "Email address or webhook URL",
                        },
                        "template": {
                            "type": "string",
                            "description": "Template name to use",
                        },
                        "events": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Events that trigger this notification",
                        },
                    },
                    "required": ["name", "type", "target", "events"],
                },
            },
        ]

    def get_ui_builder_tools(self, project_id: int = None) -> List[Dict]:
        """Genera tool per la gestione della UI tramite Visual Builder."""
        return [
            {
                "name": "create_ui_view",
                "description": "Create a new UI view (SysView) for a model. A view defines how data is presented (list, form, kanban, etc.) and contains a set of UI components.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "model_name": {
                            "type": "string",
                            "description": "Name of the model this view belongs to",
                        },
                        "view_name": {
                            "type": "string",
                            "description": "Technical name for the view (e.g., 'customer_list')",
                        },
                        "view_title": {
                            "type": "string",
                            "description": "Display title for the view",
                        },
                        "view_type": {
                            "type": "string",
                            "enum": ["list", "form", "kanban", "dashboard", "custom"],
                            "description": "Type of view",
                        },
                        "is_default": {
                            "type": "boolean",
                            "description": "Whether this should be the default view for the model",
                        },
                        "components": {
                            "type": "array",
                            "description": "Initial set of components for the view",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {
                                        "type": "string",
                                        "description": "Component type (e.g., 'table', 'form', 'chart')",
                                    },
                                    "name": {"type": "string"},
                                    "x": {"type": "integer"},
                                    "y": {"type": "integer"},
                                    "w": {"type": "integer"},
                                    "h": {"type": "integer"},
                                    "config": {
                                        "type": "object",
                                        "description": "Component-specific configuration (supports {{expressions}})",
                                    },
                                },
                                "required": ["type", "x", "y"],
                            },
                        },
                    },
                    "required": ["model_name", "view_name", "view_type"],
                },
            },
            {
                "name": "add_ui_component",
                "description": "Add a UI component to an existing view.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "view_id": {
                            "type": "integer",
                            "description": "ID of the view to modify",
                        },
                        "component": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "name": {"type": "string"},
                                "x": {"type": "integer"},
                                "y": {"type": "integer"},
                                "w": {"type": "integer"},
                                "h": {"type": "integer"},
                                "config": {"type": "object"},
                            },
                            "required": ["type", "x", "y"],
                        },
                    },
                    "required": ["view_id", "component"],
                },
            },
            {
                "name": "update_ui_view_config",
                "description": "Update the complete configuration of a UI view.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "view_id": {
                            "type": "integer",
                            "description": "ID of the view to update",
                        },
                        "components": {
                            "type": "array",
                            "description": "The new set of components for the view",
                        },
                    },
                    "required": ["view_id", "components"],
                },
            },
        ]

    def get_test_tools(self, project_id: int = None) -> List[Dict]:
        """Genera tool per la generazione automatica di test."""
        return [
            {
                "name": "generate_test_suite",
                "description": "Generate a complete test suite for a model including CRUD tests, validation tests, and API tests. The tests are saved to the database and can be executed from the Test Runner.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "model_name": {
                            "type": "string",
                            "description": "Name of the model to generate tests for",
                        },
                        "test_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Types of tests to generate: create, read, update, delete, validation",
                            "default": [
                                "create",
                                "read",
                                "update",
                                "delete",
                                "validation",
                            ],
                        },
                        "save_to_db": {
                            "type": "boolean",
                            "description": "Whether to save the test suite to the database",
                            "default": True,
                        },
                    },
                    "required": ["model_name"],
                },
            },
            {
                "name": "list_test_suites",
                "description": "List all test suites available for a project",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "integer",
                            "description": "ID of the project",
                        }
                    },
                },
            },
            {
                "name": "run_test_suite",
                "description": "Execute a test suite and get results",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "suite_id": {
                            "type": "integer",
                            "description": "ID of the test suite to run",
                        }
                    },
                    "required": ["suite_id"],
                },
            },
        ]


# Singleton instance
tool_registry = ToolRegistry()

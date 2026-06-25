"""
Command Handlers for Builder Service.

Implements CQRS pattern for handling commands.
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import asdict

logger = logging.getLogger(__name__)


class CreateModelCommand:
    """Command to create a new model."""

    def __init__(
        self,
        project_id: int,
        name: str,
        title: str,
        description: str = None,
        table_name: str = None,
        technical_name: str = None,
        permissions: Dict = None,
    ):
        self.project_id = project_id
        self.name = name
        self.title = title
        self.description = description
        self.table_name = table_name or name.lower().replace(" ", "_")
        self.technical_name = technical_name or name.lower().replace(" ", ".")
        self.permissions = permissions or {}


class AddFieldCommand:
    """Command to add a field to a model."""

    def __init__(
        self,
        model_id: int,
        name: str,
        field_type: str,
        label: str = None,
        required: bool = False,
        unique: bool = False,
        default_value: Any = None,
        options: Dict = None,
    ):
        self.model_id = model_id
        self.name = name
        self.field_type = field_type
        self.label = label or name
        self.required = required
        self.unique = unique
        self.default_value = default_value
        self.options = options or {}


class UpdateFieldCommand:
    """Command to update a field."""

    def __init__(self, field_id: int, changes: Dict[str, Any]):
        self.field_id = field_id
        self.changes = changes


class DeleteFieldCommand:
    """Command to delete a field."""

    def __init__(self, field_id: int):
        self.field_id = field_id


class SyncSchemaCommand:
    """Command to sync model schema to database."""

    def __init__(self, model_id: int, db_engine=None):
        self.model_id = model_id
        self.db_engine = db_engine


class UpdateModelCommand:
    """Command to update a model."""

    def __init__(self, model_id: int, changes: Dict[str, Any]):
        self.model_id = model_id
        self.changes = changes


class DeleteModelCommand:
    """Command to delete a model."""

    def __init__(self, model_id: int):
        self.model_id = model_id


class CommandHandler:
    """Handles model commands."""

    def __init__(self, repository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus

    def handle_create_model(self, command: CreateModelCommand) -> Dict[str, Any]:
        """Handle create model command."""
        model_data = {
            "project_id": command.project_id,
            "name": command.name,
            "title": command.title,
            "description": command.description,
            "table_name": command.table_name,
            "technical_name": command.technical_name,
            "permissions": command.permissions,
            "status": "draft",
        }

        result = self.repository.save(model_data)

        if self.event_bus and result.get("id"):
            from .model_events import ModelCreatedEvent

            event = ModelCreatedEvent(
                model_id=result["id"],
                model_name=result["name"],
                project_id=command.project_id,
            )
            self.event_bus.publish(event)

        return result

    def handle_add_field(self, command: AddFieldCommand) -> Dict[str, Any]:
        """Handle add field command."""
        field_data = {
            "model_id": command.model_id,
            "name": command.name,
            "technical_name": command.name.lower().replace(" ", "_"),
            "type": command.field_type,
            "label": command.label,
            "required": command.required,
            "unique": command.unique,
            "default_value": command.default_value,
            "options": command.options,
        }

        result = self.repository.add_field(command.model_id, field_data)

        if self.event_bus and result.get("id"):
            from .model_events import FieldAddedEvent

            event = FieldAddedEvent(
                model_id=command.model_id,
                field_id=result["id"],
                field_name=result.get("name", ""),
                field_type=command.field_type,
            )
            self.event_bus.publish(event)

        return result

    def handle_update_field(self, command: UpdateFieldCommand) -> Dict[str, Any]:
        """Handle update field command."""
        return self.repository.update_field(command.field_id, command.changes)

    def handle_delete_field(self, command: DeleteFieldCommand) -> Dict[str, Any]:
        """Handle delete field command."""
        result = self.repository.delete_field(command.field_id)

        if self.event_bus and result.get("success"):
            from .model_events import FieldDeletedEvent

            event = FieldDeletedEvent(
                field_id=command.field_id,
                field_name=result.get("field_name", ""),
            )
            self.event_bus.publish(event)

        return result

    def handle_update_model(self, command: UpdateModelCommand) -> Dict[str, Any]:
        """Handle update model command."""
        return self.repository.update(command.model_id, command.changes)

    def handle_delete_model(self, command: DeleteModelCommand) -> Dict[str, Any]:
        """Handle delete model command."""
        result = self.repository.delete(command.model_id)

        if self.event_bus and result.get("success"):
            from .model_events import ModelDeletedEvent

            event = ModelDeletedEvent(
                model_id=command.model_id,
                model_name=result.get("model_name", ""),
            )
            self.event_bus.publish(event)

        return result

    def handle_sync_schema(self, command: SyncSchemaCommand) -> Dict[str, Any]:
        """Handle sync schema command."""
        model = self.repository.find_by_id(command.model_id)

        if not model:
            return {"success": False, "error": "Model not found"}

        from backend.utils import generate_schema_diff_sql
        from backend.extensions import db

        sys_model = model
        db_engine = command.db_engine or db.engine

        sql_commands = generate_schema_diff_sql(sys_model, db_engine)

        result = {"success": True, "sql_commands": sql_commands}

        if self.event_bus:
            from .model_events import SchemaSyncedEvent

            event = SchemaSyncedEvent(
                model_id=command.model_id,
                model_name=model.get("name", ""),
                changes={"commands_count": len(sql_commands)},
            )
            self.event_bus.publish(event)

        return result

"""
Model Service - Domain service for Builder operations.
"""

import logging
from typing import List, Dict, Any, Optional

from ..domain.entities.model_definition import ModelDefinition, FieldDefinition
from ..domain.repositories.model_repository import ModelRepository
from ..application.commands.create_model import (
    CommandHandler,
    CreateModelCommand,
    AddFieldCommand,
    UpdateFieldCommand,
    DeleteFieldCommand,
    UpdateModelCommand,
    DeleteModelCommand,
    SyncSchemaCommand,
)
from ..application.queries.get_model import (
    QueryHandler,
    GetModelQuery,
    ListModelsQuery,
    GetFieldsQuery,
)

logger = logging.getLogger(__name__)


class ModelService:
    """
    Main service for model operations.
    Combines Command and Query responsibilities.
    """

    def __init__(self, repository: ModelRepository, event_bus=None):
        self.repository = repository
        self.command_handler = CommandHandler(repository, event_bus)
        self.query_handler = QueryHandler(repository)

    def get_model(
        self, model_id: int = None, technical_name: str = None, project_id: int = None
    ) -> Optional[Dict]:
        """Get a single model."""
        query = GetModelQuery(model_id, technical_name, project_id)
        return self.query_handler.handle_get_model(query)

    def list_models(
        self,
        project_id: int,
        status: str = None,
        search: str = None,
        page: int = 1,
        per_page: int = 20,
    ) -> Dict:
        """List models in a project."""
        query = ListModelsQuery(project_id, status, search, page, per_page)
        return self.query_handler.handle_list_models(query)

    def create_model(
        self,
        project_id: int,
        name: str,
        title: str,
        description: str = None,
        table_name: str = None,
        technical_name: str = None,
        permissions: Dict = None,
    ) -> Dict:
        """Create a new model."""
        command = CreateModelCommand(
            project_id=project_id,
            name=name,
            title=title,
            description=description,
            table_name=table_name,
            technical_name=technical_name,
            permissions=permissions,
        )
        return self.command_handler.handle_create_model(command)

    def update_model(self, model_id: int, changes: Dict[str, Any]) -> Dict:
        """Update a model."""
        command = UpdateModelCommand(model_id, changes)
        return self.command_handler.handle_update_model(command)

    def delete_model(self, model_id: int) -> Dict:
        """Delete a model."""
        command = DeleteModelCommand(model_id)
        return self.command_handler.handle_delete_model(command)

    def add_field(
        self,
        model_id: int,
        name: str,
        field_type: str,
        label: str = None,
        required: bool = False,
        unique: bool = False,
        default_value: Any = None,
        options: Dict = None,
    ) -> Dict:
        """Add a field to a model."""
        command = AddFieldCommand(
            model_id=model_id,
            name=name,
            field_type=field_type,
            label=label,
            required=required,
            unique=unique,
            default_value=default_value,
            options=options,
        )
        return self.command_handler.handle_add_field(command)

    def update_field(self, field_id: int, changes: Dict[str, Any]) -> Dict:
        """Update a field."""
        command = UpdateFieldCommand(field_id, changes)
        return self.command_handler.handle_update_field(command)

    def delete_field(self, field_id: int) -> Dict:
        """Delete a field."""
        command = DeleteFieldCommand(field_id)
        return self.command_handler.handle_delete_field(command)

    def get_fields(self, model_id: int) -> List[Dict]:
        """Get all fields for a model."""
        query = GetFieldsQuery(model_id)
        return self.query_handler.handle_get_fields(query)

    def sync_schema(self, model_id: int, db_engine=None) -> Dict:
        """Sync model schema to database."""
        command = SyncSchemaCommand(model_id, db_engine)
        return self.command_handler.handle_sync_schema(command)

    def clone_model(self, model_id: int, new_name: str, new_title: str) -> Dict:
        """Clone a model with a new name."""
        original = self.get_model(model_id)

        if not original:
            return {"success": False, "error": "Model not found"}

        return self.create_model(
            project_id=original["project_id"],
            name=new_name,
            title=new_title,
            description=original.get("description"),
            permissions=original.get("permissions"),
        )

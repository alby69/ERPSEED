"""
Builder API - REST API for Builder Service.

This module provides Flask-Smorest Blueprint for Builder operations:
- Models: CRUD for data models (SysModel, SysField)
- Archetypes: CRUD for component archetypes
- Components: CRUD for UI components
- Blocks: CRUD for page blocks
"""
import logging
from typing import Dict, Any, Optional
from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields

from backend.shared.handlers import CommandResult
from backend.application.builder.commands import (
    CreateModelCommand, UpdateModelCommand, DeleteModelCommand, AddFieldCommand, DeleteFieldCommand,
    GetModelCommand, ListModelsCommand, GenerateCodeCommand,
    CreateArchetypeCommand, UpdateArchetypeCommand, DeleteArchetypeCommand, GetArchetypeCommand, ListArchetypesCommand,
    CreateComponentCommand, UpdateComponentCommand, DeleteComponentCommand, GetComponentCommand, ListComponentsCommand,
    CreateBlockCommand, UpdateBlockCommand, DeleteBlockCommand, GetBlockCommand, ListBlocksCommand, ConvertToTemplateCommand,
)
from backend.application.builder.handlers import (
    CreateModelHandler, UpdateModelHandler, DeleteModelHandler, AddFieldHandler, DeleteFieldHandler,
    GetModelHandler, ListModelsHandler, GenerateCodeHandler,
    CreateArchetypeHandler, UpdateArchetypeHandler, DeleteArchetypeHandler, GetArchetypeHandler, ListArchetypesHandler,
    CreateComponentHandler, UpdateComponentHandler, DeleteComponentHandler, GetComponentHandler, ListComponentsHandler,
    CreateBlockHandler, UpdateBlockHandler, DeleteBlockHandler, GetBlockHandler, ListBlocksHandler, ConvertToTemplateHandler,
)
from backend.infrastructure.builder.repository import ModelRepository, ArchetypeRepository, ComponentRepository, BlockRepository

logger = logging.getLogger(__name__)

blp = Blueprint("builder", __name__, url_prefix="/api/builder", description="Builder Service API")


class BuilderCommandExecutor:
    """Executes CQRS commands for Builder service."""
    
    COMMAND_HANDLERS = {
        # Model commands
        "CreateModel": CreateModelHandler,
        "UpdateModel": UpdateModelHandler,
        "DeleteModel": DeleteModelHandler,
        "AddField": AddFieldHandler,
        "DeleteField": AddFieldHandler,
        "GetModel": GetModelHandler,
        "ListModels": ListModelsHandler,
        "GenerateCode": GenerateCodeHandler,
        # Archetype commands
        "CreateArchetype": CreateArchetypeHandler,
        "UpdateArchetype": UpdateArchetypeHandler,
        "DeleteArchetype": DeleteArchetypeHandler,
        "GetArchetype": GetArchetypeHandler,
        "ListArchetypes": ListArchetypesHandler,
        # Component commands
        "CreateComponent": CreateComponentHandler,
        "UpdateComponent": UpdateComponentHandler,
        "DeleteComponent": DeleteComponentHandler,
        "GetComponent": GetComponentHandler,
        "ListComponents": ListComponentsHandler,
        # Block commands
        "CreateBlock": CreateBlockHandler,
        "UpdateBlock": UpdateBlockHandler,
        "DeleteBlock": DeleteBlockHandler,
        "GetBlock": GetBlockHandler,
        "ListBlocks": ListBlocksHandler,
        "ConvertToTemplate": ConvertToTemplateHandler,
    }
    
    REPO_MAP = {
        "Model": "model",
        "Archetype": "archetype",
        "Component": "component",
        "Block": "block",
    }
    
    def __init__(self):
        self._handlers = {}
        self._repositories = {}
    
    def _get_repository(self, command_name: str):
        entity_type = command_name.replace("Create", "").replace("Update", "").replace("Delete", "").replace("Get", "").replace("List", "").replace("Add", "").replace("Generate", "")
        repo_key = self.REPO_MAP.get(entity_type, "")
        
        if not hasattr(self, '_db'):
            from backend.extensions import db
            self._db = db
        
        if repo_key not in self._repositories:
            if repo_key == "model":
                self._repositories[repo_key] = ModelRepository(db=self._db)
            elif repo_key == "archetype":
                self._repositories[repo_key] = ArchetypeRepository(db=self._db)
            elif repo_key == "component":
                self._repositories[repo_key] = ComponentRepository(db=self._db)
            elif repo_key == "block":
                self._repositories[repo_key] = BlockRepository(db=self._db)
        
        return self._repositories.get(repo_key)
    
    def _get_handler(self, command_name: str):
        if command_name not in self._handlers:
            handler_class = self.COMMAND_HANDLERS.get(command_name)
            if not handler_class:
                return None
            repo = self._get_repository(command_name)
            self._handlers[command_name] = handler_class(repository=repo)
        return self._handlers[command_name]
    
    def execute(self, command_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        handler = self._get_handler(command_name)
        if not handler:
            return CommandResult.error(f"Unknown command: {command_name}").to_dict()
        
        command_classes = {
            "CreateModel": CreateModelCommand, "UpdateModel": UpdateModelCommand,
            "DeleteModel": DeleteModelCommand, "AddField": AddFieldCommand, "DeleteField": DeleteFieldCommand,
            "GetModel": GetModelCommand, "ListModels": ListModelsCommand, "GenerateCode": GenerateCodeCommand,
            "CreateArchetype": CreateArchetypeCommand, "UpdateArchetype": UpdateArchetypeCommand,
            "DeleteArchetype": DeleteArchetypeCommand, "GetArchetype": GetArchetypeCommand, "ListArchetypes": ListArchetypesCommand,
            "CreateComponent": CreateComponentCommand, "UpdateComponent": UpdateComponentCommand,
            "DeleteComponent": DeleteComponentCommand, "GetComponent": GetComponentCommand, "ListComponents": ListComponentsCommand,
            "CreateBlock": CreateBlockCommand, "UpdateBlock": UpdateBlockCommand,
            "DeleteBlock": DeleteBlockCommand, "GetBlock": GetBlockCommand, "ListBlocks": ListBlocksCommand,
            "ConvertToTemplate": ConvertToTemplateCommand,
        }
        
        command_class = command_classes.get(command_name)
        if not command_class:
            return CommandResult.error(f"Unknown command: {command_name}").to_dict()
        
        try:
            cmd = command_class.from_dict(data)
            result = handler.handle(cmd)
            return result.to_dict() if hasattr(result, 'to_dict') else result
        except Exception as e:
            logger.error(f"Error executing {command_name}: {e}", exc_info=True)
            return CommandResult.error(f"Internal error: {str(e)}").to_dict()


_executor = None


def get_executor() -> BuilderCommandExecutor:
    global _executor
    if _executor is None:
        _executor = BuilderCommandExecutor()
    return _executor


# === MODEL ENDPOINTS ===

@blp.route("/models")
class ModelList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """List all models."""
        executor = get_executor()
        data = request.args.to_dict()
        return executor.execute("ListModels", data)
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        """Create a new model."""
        executor = get_executor()
        return executor.execute("CreateModel", request.get_json() or {})


@blp.route("/models/<int:model_id>")
class ModelDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, model_id):
        """Get model by ID."""
        executor = get_executor()
        return executor.execute("GetModel", {"entity_id": model_id})
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, model_id):
        """Update model."""
        executor = get_executor()
        data = request.get_json() or {}
        data["entity_id"] = model_id
        return executor.execute("UpdateModel", data)
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, model_id):
        """Delete model."""
        executor = get_executor()
        return executor.execute("DeleteModel", {"entity_id": model_id})


@blp.route("/models/<int:model_id>/fields")
class ModelFields(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, model_id):
        """Add field to model."""
        executor = get_executor()
        data = request.get_json() or {}
        data["model_id"] = model_id
        return executor.execute("AddField", data)


@blp.route("/models/<int:model_id>/generate-code")
class ModelGenerateCode(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, model_id):
        """Generate code for model."""
        executor = get_executor()
        data = request.get_json() or {}
        data["model_id"] = model_id
        return executor.execute("GenerateCode", data)


# === ARCHETYPE ENDPOINTS ===

@blp.route("/archetypes")
class ArchetypeList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """List all archetypes."""
        executor = get_executor()
        return executor.execute("ListArchetypes", request.args.to_dict())
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        """Create a new archetype."""
        executor = get_executor()
        return executor.execute("CreateArchetype", request.get_json() or {})


@blp.route("/archetypes/<int:archetype_id>")
class ArchetypeDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, archetype_id):
        """Get archetype by ID."""
        executor = get_executor()
        return executor.execute("GetArchetype", {"entity_id": archetype_id})
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, archetype_id):
        """Update archetype."""
        executor = get_executor()
        data = request.get_json() or {}
        data["entity_id"] = archetype_id
        return executor.execute("UpdateArchetype", data)
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, archetype_id):
        """Delete archetype."""
        executor = get_executor()
        return executor.execute("DeleteArchetype", {"entity_id": archetype_id})


# === COMPONENT ENDPOINTS ===

@blp.route("/components")
class ComponentList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """List all components."""
        executor = get_executor()
        return executor.execute("ListComponents", request.args.to_dict())
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        """Create a new component."""
        executor = get_executor()
        return executor.execute("CreateComponent", request.get_json() or {})


@blp.route("/components/<int:component_id>")
class ComponentDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, component_id):
        """Get component by ID."""
        executor = get_executor()
        return executor.execute("GetComponent", {"entity_id": component_id})
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, component_id):
        """Update component."""
        executor = get_executor()
        data = request.get_json() or {}
        data["entity_id"] = component_id
        return executor.execute("UpdateComponent", data)
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, component_id):
        """Delete component."""
        executor = get_executor()
        return executor.execute("DeleteComponent", {"entity_id": component_id})


# === BLOCK ENDPOINTS ===

@blp.route("/blocks")
class BlockList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """List all blocks."""
        executor = get_executor()
        return executor.execute("ListBlocks", request.args.to_dict())
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        """Create a new block."""
        executor = get_executor()
        return executor.execute("CreateBlock", request.get_json() or {})


@blp.route("/blocks/<int:block_id>")
class BlockDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, block_id):
        """Get block by ID."""
        executor = get_executor()
        return executor.execute("GetBlock", {"entity_id": block_id})
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, block_id):
        """Update block."""
        executor = get_executor()
        data = request.get_json() or {}
        data["entity_id"] = block_id
        return executor.execute("UpdateBlock", data)
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, block_id):
        """Delete block."""
        executor = get_executor()
        return executor.execute("DeleteBlock", {"entity_id": block_id})


@blp.route("/blocks/<int:block_id>/convert-to-template")
class BlockConvertToTemplate(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, block_id):
        """Convert block to template."""
        executor = get_executor()
        data = request.get_json() or {}
        data["entity_id"] = block_id
        return executor.execute("ConvertToTemplate", data)

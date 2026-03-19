"""
Builder Handlers - Model, Component, Block, Archetype.
"""
import logging
from backend.shared.handlers import CommandHandler, CommandResult, CreateHandler, UpdateHandler, QueryHandler
from backend.shared.commands import Command

from backend.application.builder.commands import (
    CreateModelCommand, UpdateModelCommand, DeleteModelCommand, AddFieldCommand, DeleteFieldCommand,
    GetModelCommand, ListModelsCommand, GenerateCodeCommand,
    CreateArchetypeCommand, GetArchetypeCommand, ListArchetypesCommand,
    CreateComponentCommand, ListComponentsCommand,
    CreateBlockCommand, GetBlockCommand, ListBlocksCommand, ConvertToTemplateCommand,
)
from backend.domain.builder import (
    generate_model, generate_api, generate_crud_service, generate_module,
    ModelCreatedEvent, BlockCreatedEvent
)
from backend.infrastructure.builder.repository import ModelRepository, ArchetypeRepository, ComponentRepository, BlockRepository

logger = logging.getLogger(__name__)


class CreateModelHandler(CreateHandler):
    def __init__(self, repository: ModelRepository, event_bus=None):
        self.repository = repository; self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "CreateModel"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, CreateModelCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        try:
            result = self.repository.save(command.to_payload())
            if self.event_bus and result.get("id"):
                self.event_bus.publish(ModelCreatedEvent(result["id"], result.get("name", ""), command.project_id))
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error creating model: {e}")
            return CommandResult.error(f"Failed to create model: {str(e)}")


class UpdateModelHandler(UpdateHandler):
    def __init__(self, repository: ModelRepository, event_bus=None):
        self.repository = repository; self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "UpdateModel"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, UpdateModelCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        if not command.entity_id: return CommandResult.error("Model ID is required")
        try:
            result = self.repository.update(command.entity_id, command.to_payload())
            if not result: return CommandResult.error(f"Model not found: {command.entity_id}")
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error updating model: {e}")
            return CommandResult.error(f"Failed to update model: {str(e)}")


class DeleteModelHandler(CommandHandler):
    def __init__(self, repository: ModelRepository, event_bus=None):
        self.repository = repository; self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "DeleteModel"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, DeleteModelCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        if not command.entity_id: return CommandResult.error("Model ID is required")
        try:
            result = self.repository.delete(command.entity_id)
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error deleting model: {e}")
            return CommandResult.error(f"Failed to delete model: {str(e)}")


class AddFieldHandler(CommandHandler):
    def __init__(self, repository: ModelRepository, event_bus=None):
        self.repository = repository; self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "AddField"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, AddFieldCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        if not command.model_id: return CommandResult.error("Model ID is required")
        try:
            field_data = {"name": command.name, "type": command.field_type, "label": command.label,
                "required": command.required, "unique": command.unique, "default_value": command.default_value, "options": command.options}
            result = self.repository.add_field(command.model_id, field_data)
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error adding field: {e}")
            return CommandResult.error(f"Failed to add field: {str(e)}")


class GetModelHandler(QueryHandler):
    def __init__(self, repository: ModelRepository, event_bus=None):
        self.repository = repository; self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "GetModel"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, GetModelCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        if not command.entity_id: return CommandResult.error("Model ID is required")
        result = self.repository.find_by_id(command.entity_id)
        if not result: return CommandResult.error(f"Model not found: {command.entity_id}")
        return CommandResult.ok(result)


class ListModelsHandler(QueryHandler):
    def __init__(self, repository: ModelRepository, event_bus=None):
        self.repository = repository; self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "ListModels"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, ListModelsCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        try:
            result = self.repository.find_all(project_id=command.project_id)
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return CommandResult.error(f"Failed to list models: {str(e)}")


class GenerateCodeHandler(CommandHandler):
    def __init__(self, repository: ModelRepository, event_bus=None):
        self.repository = repository; self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "GenerateCode"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, GenerateCodeCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        if not command.model_id: return CommandResult.error("Model ID is required")
        model = self.repository.find_by_id(command.model_id)
        if not model: return CommandResult.error(f"Model not found: {command.model_id}")
        try:
            result = {}
            if command.include_api or command.include_service:
                result = generate_module(model, command.api_prefix)
            else:
                result = {"model": generate_model(model)}
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            return CommandResult.error(f"Failed to generate code: {str(e)}")


class CreateArchetypeHandler(CreateHandler):
    def __init__(self, repository: ArchetypeRepository, event_bus=None):
        self.repository = repository; self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "CreateArchetype"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, CreateArchetypeCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        try:
            result = self.repository.create(command.to_payload())
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error creating archetype: {e}")
            return CommandResult.error(f"Failed to create archetype: {str(e)}")


class ListArchetypesHandler(QueryHandler):
    def __init__(self, repository: ArchetypeRepository, event_bus=None):
        self.repository = repository; self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "ListArchetypes"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, ListArchetypesCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        try:
            result = self.repository.find_all()
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error listing archetypes: {e}")
            return CommandResult.error(f"Failed to list archetypes: {str(e)}")


class CreateComponentHandler(CreateHandler):
    def __init__(self, repository: ComponentRepository, event_bus=None):
        self.repository = repository; self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "CreateComponent"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, CreateComponentCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        try:
            result = self.repository.create(command.to_payload())
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error creating component: {e}")
            return CommandResult.error(f"Failed to create component: {str(e)}")


class ListComponentsHandler(QueryHandler):
    def __init__(self, repository: ComponentRepository, event_bus=None):
        self.repository = repository; self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "ListComponents"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, ListComponentsCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        try:
            result = self.repository.find_all(project_id=command.project_id, block_id=command.block_id)
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error listing components: {e}")
            return CommandResult.error(f"Failed to list components: {str(e)}")


class CreateBlockHandler(CreateHandler):
    def __init__(self, repository: BlockRepository, event_bus=None):
        self.repository = repository; self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "CreateBlock"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, CreateBlockCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        try:
            result = self.repository.create(command.to_payload())
            if self.event_bus and result.get("id"):
                self.event_bus.publish(BlockCreatedEvent(result["id"], result.get("name", ""), command.project_id))
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error creating block: {e}")
            return CommandResult.error(f"Failed to create block: {str(e)}")


class GetBlockHandler(QueryHandler):
    def __init__(self, repository: BlockRepository, event_bus=None):
        self.repository = repository; self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "GetBlock"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, GetBlockCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        if not command.entity_id: return CommandResult.error("Block ID is required")
        result = self.repository.find_by_id(command.entity_id)
        if not result: return CommandResult.error(f"Block not found: {command.entity_id}")
        return CommandResult.ok(result)


class ListBlocksHandler(QueryHandler):
    def __init__(self, repository: BlockRepository, event_bus=None):
        self.repository = repository; self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "ListBlocks"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, ListBlocksCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        try:
            result = self.repository.find_all(project_id=command.project_id, include_templates=command.include_templates)
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error listing blocks: {e}")
            return CommandResult.error(f"Failed to list blocks: {str(e)}")


class ConvertToTemplateHandler(UpdateHandler):
    def __init__(self, repository: BlockRepository, event_bus=None):
        self.repository = repository; self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "ConvertToTemplate"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, ConvertToTemplateCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        if not command.entity_id: return CommandResult.error("Block ID is required")
        try:
            result = self.repository.update(command.entity_id, command.to_payload())
            if not result: return CommandResult.error(f"Block not found: {command.entity_id}")
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error converting to template: {e}")
            return CommandResult.error(f"Failed to convert to template: {str(e)}")

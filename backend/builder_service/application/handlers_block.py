"""
Builder Handlers - Handlers for Block, Component, Archetype commands.
"""
import logging
from backend.shared.handlers import CommandHandler, CommandResult, CreateHandler, UpdateHandler, DeleteHandler, QueryHandler
from backend.shared.commands import Command
from backend.builder_service.application.commands.block_components import (
    CreateArchetypeCommand, UpdateArchetypeCommand, DeleteArchetypeCommand, GetArchetypeCommand, ListArchetypesCommand,
    CreateComponentCommand, UpdateComponentCommand, DeleteComponentCommand, GetComponentCommand, ListComponentsCommand,
    CreateBlockCommand, UpdateBlockCommand, DeleteBlockCommand, GetBlockCommand, ListBlocksCommand
)
from backend.builder_service.infrastructure.block_repository import ArchetypeRepository, ComponentRepository, BlockRepository
from backend.shared.events.event import DomainEvent

logger = logging.getLogger(__name__)


# === ARCHETYPE HANDLERS ===
class CreateArchetypeHandler(CreateHandler):
    def __init__(self, repository: ArchetypeRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "CreateArchetype"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, CreateArchetypeCommand): return CommandResult.error(f"Invalid command type")
        try:
            result = self.repository.create(command.to_payload())
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error creating archetype: {e}")
            return CommandResult.error(f"Failed to create archetype: {str(e)}")


class UpdateArchetypeHandler(UpdateHandler):
    def __init__(self, repository: ArchetypeRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "UpdateArchetype"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, UpdateArchetypeCommand): return CommandResult.error(f"Invalid command type")
        if not command.entity_id: return CommandResult.error("Archetype ID is required")
        try:
            result = self.repository.update(command.entity_id, command.to_payload())
            if not result: return CommandResult.error(f"Archetype not found")
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error updating archetype: {e}")
            return CommandResult.error(f"Failed to update archetype: {str(e)}")


class DeleteArchetypeHandler(DeleteHandler):
    def __init__(self, repository: ArchetypeRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "DeleteArchetype"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, DeleteArchetypeCommand): return CommandResult.error(f"Invalid command type")
        if not command.entity_id: return CommandResult.error("Archetype ID is required")
        try:
            result = self.repository.delete(command.entity_id)
            if not result: return CommandResult.error(f"Archetype not found")
            return CommandResult.ok({"deleted": True, "archetype_id": command.entity_id})
        except Exception as e:
            logger.error(f"Error deleting archetype: {e}")
            return CommandResult.error(f"Failed to delete archetype: {str(e)}")


class GetArchetypeHandler(QueryHandler):
    def __init__(self, repository: ArchetypeRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "GetArchetype"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, GetArchetypeCommand): return CommandResult.error(f"Invalid command type")
        if not command.entity_id: return CommandResult.error("Archetype ID is required")
        result = self.repository.find_by_id(command.entity_id)
        if not result: return CommandResult.error(f"Archetype not found")
        return CommandResult.ok(result)


class ListArchetypesHandler(QueryHandler):
    def __init__(self, repository: ArchetypeRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "ListArchetypes"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, ListArchetypesCommand): return CommandResult.error(f"Invalid command type")
        try:
            pagination = command.pagination or {}
            result = self.repository.find_all(page=pagination.get("page", 1), per_page=pagination.get("per_page", 20))
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error listing archetypes: {e}")
            return CommandResult.error(f"Failed to list archetypes: {str(e)}")


# === COMPONENT HANDLERS ===
class CreateComponentHandler(CreateHandler):
    def __init__(self, repository: ComponentRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "CreateComponent"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, CreateComponentCommand): return CommandResult.error(f"Invalid command type")
        try:
            result = self.repository.create(command.to_payload())
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error creating component: {e}")
            return CommandResult.error(f"Failed to create component: {str(e)}")


class UpdateComponentHandler(UpdateHandler):
    def __init__(self, repository: ComponentRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "UpdateComponent"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, UpdateComponentCommand): return CommandResult.error(f"Invalid command type")
        if not command.entity_id: return CommandResult.error("Component ID is required")
        try:
            result = self.repository.update(command.entity_id, command.to_payload())
            if not result: return CommandResult.error(f"Component not found")
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error updating component: {e}")
            return CommandResult.error(f"Failed to update component: {str(e)}")


class DeleteComponentHandler(DeleteHandler):
    def __init__(self, repository: ComponentRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "DeleteComponent"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, DeleteComponentCommand): return CommandResult.error(f"Invalid command type")
        if not command.entity_id: return CommandResult.error("Component ID is required")
        try:
            result = self.repository.delete(command.entity_id)
            if not result: return CommandResult.error(f"Component not found")
            return CommandResult.ok({"deleted": True, "component_id": command.entity_id})
        except Exception as e:
            logger.error(f"Error deleting component: {e}")
            return CommandResult.error(f"Failed to delete component: {str(e)}")


class GetComponentHandler(QueryHandler):
    def __init__(self, repository: ComponentRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "GetComponent"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, GetComponentCommand): return CommandResult.error(f"Invalid command type")
        if not command.entity_id: return CommandResult.error("Component ID is required")
        result = self.repository.find_by_id(command.entity_id)
        if not result: return CommandResult.error(f"Component not found")
        return CommandResult.ok(result)


class ListComponentsHandler(QueryHandler):
    def __init__(self, repository: ComponentRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "ListComponents"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, ListComponentsCommand): return CommandResult.error(f"Invalid command type")
        try:
            filters = command.filters or {}
            pagination = command.pagination or {}
            result = self.repository.find_all(project_id=filters.get("project_id", command.project_id),
                block_id=filters.get("block_id", command.block_id),
                page=pagination.get("page", 1), per_page=pagination.get("per_page", 20))
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error listing components: {e}")
            return CommandResult.error(f"Failed to list components: {str(e)}")


# === BLOCK HANDLERS ===
class CreateBlockHandler(CreateHandler):
    def __init__(self, repository: BlockRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "CreateBlock"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, CreateBlockCommand): return CommandResult.error(f"Invalid command type")
        try:
            result = self.repository.create(command.to_payload())
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error creating block: {e}")
            return CommandResult.error(f"Failed to create block: {str(e)}")


class UpdateBlockHandler(UpdateHandler):
    def __init__(self, repository: BlockRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "UpdateBlock"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, UpdateBlockCommand): return CommandResult.error(f"Invalid command type")
        if not command.entity_id: return CommandResult.error("Block ID is required")
        try:
            result = self.repository.update(command.entity_id, command.to_payload())
            if not result: return CommandResult.error(f"Block not found")
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error updating block: {e}")
            return CommandResult.error(f"Failed to update block: {str(e)}")


class DeleteBlockHandler(DeleteHandler):
    def __init__(self, repository: BlockRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "DeleteBlock"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, DeleteBlockCommand): return CommandResult.error(f"Invalid command type")
        if not command.entity_id: return CommandResult.error("Block ID is required")
        try:
            result = self.repository.delete(command.entity_id)
            if not result: return CommandResult.error(f"Block not found")
            return CommandResult.ok({"deleted": True, "block_id": command.entity_id})
        except Exception as e:
            logger.error(f"Error deleting block: {e}")
            return CommandResult.error(f"Failed to delete block: {str(e)}")


class GetBlockHandler(QueryHandler):
    def __init__(self, repository: BlockRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "GetBlock"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, GetBlockCommand): return CommandResult.error(f"Invalid command type")
        if not command.entity_id: return CommandResult.error("Block ID is required")
        result = self.repository.find_by_id(command.entity_id)
        if not result: return CommandResult.error(f"Block not found")
        return CommandResult.ok(result)


class ListBlocksHandler(QueryHandler):
    def __init__(self, repository: BlockRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "ListBlocks"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, ListBlocksCommand): return CommandResult.error(f"Invalid command type")
        try:
            filters = command.filters or {}
            pagination = command.pagination or {}
            result = self.repository.find_all(project_id=filters.get("project_id", command.project_id),
                status=filters.get("status", command.status),
                page=pagination.get("page", 1), per_page=pagination.get("per_page", 20))
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error listing blocks: {e}")
            return CommandResult.error(f"Failed to list blocks: {str(e)}")

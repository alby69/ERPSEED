"""
Builder Service API - Main entry point for Builder Service with Block/Component/Archetype.
"""
import logging
from typing import Dict, Any, Optional
from backend.shared.handlers import CommandResult
from backend.builder_service.application.commands.block_components import (
    CreateArchetypeCommand, UpdateArchetypeCommand, DeleteArchetypeCommand, GetArchetypeCommand, ListArchetypesCommand,
    CreateComponentCommand, UpdateComponentCommand, DeleteComponentCommand, GetComponentCommand, ListComponentsCommand,
    CreateBlockCommand, UpdateBlockCommand, DeleteBlockCommand, GetBlockCommand, ListBlocksCommand
)
from backend.builder_service.application.handlers_block import (
    CreateArchetypeHandler, UpdateArchetypeHandler, DeleteArchetypeHandler, GetArchetypeHandler, ListArchetypesHandler,
    CreateComponentHandler, UpdateComponentHandler, DeleteComponentHandler, GetComponentHandler, ListComponentsHandler,
    CreateBlockHandler, UpdateBlockHandler, DeleteBlockHandler, GetBlockHandler, ListBlocksHandler
)
from backend.builder_service.container import get_builder_container
from backend.shared.events.event_bus import EventBus

logger = logging.getLogger(__name__)


class BuilderService:
    COMMAND_HANDLERS = {
        # Archetype
        "CreateArchetype": CreateArchetypeHandler,
        "UpdateArchetype": UpdateArchetypeHandler,
        "DeleteArchetype": DeleteArchetypeHandler,
        "GetArchetype": GetArchetypeHandler,
        "ListArchetypes": ListArchetypesHandler,
        # Component
        "CreateComponent": CreateComponentHandler,
        "UpdateComponent": UpdateComponentHandler,
        "DeleteComponent": DeleteComponentHandler,
        "GetComponent": GetComponentHandler,
        "ListComponents": ListComponentsHandler,
        # Block
        "CreateBlock": CreateBlockHandler,
        "UpdateBlock": UpdateBlockHandler,
        "DeleteBlock": DeleteBlockHandler,
        "GetBlock": GetBlockHandler,
        "ListBlocks": ListBlocksHandler,
    }
    
    REPO_MAP = {
        "Archetype": "archetype",
        "Component": "component", 
        "Block": "block",
    }
    
    def __init__(self, event_bus: EventBus = None):
        self._event_bus = event_bus
        self._handlers = {}
        self._container = get_builder_container()
    
    def _get_repository(self, command_name: str):
        name = command_name.replace("Create", "").replace("Update", "").replace("Delete", "").replace("Get", "").replace("List", "")
        repo_key = self.REPO_MAP.get(name, "")
        if repo_key == "archetype":
            return self._container.get_archetype_repository()
        elif repo_key == "component":
            return self._container.get_component_repository()
        elif repo_key == "block":
            return self._container.get_block_repository()
        return None
    
    def _get_handler(self, command_name: str):
        if command_name not in self._handlers:
            handler_class = self.COMMAND_HANDLERS.get(command_name)
            if not handler_class:
                return None
            repo = self._get_repository(command_name)
            self._handlers[command_name] = handler_class(repository=repo, event_bus=self._event_bus)
        return self._handlers[command_name]
    
    def execute(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        command_name = command_data.get("command")
        if not command_name:
            return CommandResult.error("Command name is required").to_dict()
        
        handler = self._get_handler(command_name)
        if not handler:
            return CommandResult.error(f"Unknown command: {command_name}").to_dict()
        
        command = self._parse_command(command_name, command_data)
        if isinstance(command, CommandResult):
            return command.to_dict()
        
        try:
            result = handler.handle(command)
            return result.to_dict()
        except Exception as e:
            logger.error(f"Error executing {command_name}: {e}", exc_info=True)
            return CommandResult.error(f"Internal error: {str(e)}").to_dict()
    
    def _parse_command(self, command_name: str, data: Dict[str, Any]):
        command_classes = {
            "CreateArchetype": CreateArchetypeCommand, "UpdateArchetype": UpdateArchetypeCommand,
            "DeleteArchetype": DeleteArchetypeCommand, "GetArchetype": GetArchetypeCommand, "ListArchetypes": ListArchetypesCommand,
            "CreateComponent": CreateComponentCommand, "UpdateComponent": UpdateComponentCommand,
            "DeleteComponent": DeleteComponentCommand, "GetComponent": GetComponentCommand, "ListComponents": ListComponentsCommand,
            "CreateBlock": CreateBlockCommand, "UpdateBlock": UpdateBlockCommand,
            "DeleteBlock": DeleteBlockCommand, "GetBlock": GetBlockCommand, "ListBlocks": ListBlocksCommand,
        }
        
        command_class = command_classes.get(command_name)
        if not command_class:
            return CommandResult.error(f"Unknown command: {command_name}")
        
        try:
            cmd = command_class.from_dict(data)
            cmd.entity_id = data.get("entity_id", data.get("id", 0))
            return cmd
        except Exception as e:
            logger.error(f"Error parsing {command_name}: {e}")
            return CommandResult.error(f"Invalid command data: {str(e)}")


_service_instance = None


def get_builder_service() -> BuilderService:
    global _service_instance
    if _service_instance is None:
        _service_instance = BuilderService()
    return _service_instance


def execute(command_data: Dict[str, Any]) -> Dict[str, Any]:
    service = get_builder_service()
    return service.execute(command_data)

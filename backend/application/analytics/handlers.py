"""
Analytics Handlers - Handle commands for Charts and Libraries.
"""
import logging
from backend.shared.handlers import CommandHandler, CommandResult, CreateHandler, UpdateHandler, DeleteHandler, QueryHandler
from backend.shared.commands import Command

from backend.application.analytics.commands import (
    CreateChartCommand, UpdateChartCommand, DeleteChartCommand, GetChartCommand, ListChartsCommand,
    CreateChartLibraryCommand, GetDefaultLibraryCommand, GetChartLibraryCommand, ListChartLibrariesCommand,
    UpdateChartLibraryCommand, DeleteChartLibraryCommand,
)
from backend.domain.analytics import ChartCreatedEvent, ChartDeletedEvent
from backend.infrastructure.analytics.repository import ChartRepository, ChartLibraryRepository

logger = logging.getLogger(__name__)


class CreateChartHandler(CreateHandler):
    def __init__(self, repository: ChartRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "CreateChart"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, CreateChartCommand): return CommandResult.error(f"Invalid command type")
        try:
            result = self.repository.create({**command.to_payload(), "tenant_id": command.tenant_id})
            if self.event_bus: self.event_bus.publish(ChartCreatedEvent(result["id"], result, command.tenant_id))
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error creating chart: {e}")
            return CommandResult.error(f"Failed to create chart: {str(e)}")


class UpdateChartHandler(UpdateHandler):
    def __init__(self, repository: ChartRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "UpdateChart"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, UpdateChartCommand): return CommandResult.error(f"Invalid command type")
        if not command.entity_id: return CommandResult.error("Chart ID is required")
        try:
            result = self.repository.update(command.entity_id, command.to_payload())
            if not result: return CommandResult.error(f"Chart not found: {command.entity_id}")
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error updating chart: {e}")
            return CommandResult.error(f"Failed to update chart: {str(e)}")


class DeleteChartHandler(DeleteHandler):
    def __init__(self, repository: ChartRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "DeleteChart"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, DeleteChartCommand): return CommandResult.error(f"Invalid command type")
        if not command.entity_id: return CommandResult.error("Chart ID is required")
        try:
            result = self.repository.delete(command.entity_id)
            if not result: return CommandResult.error(f"Chart not found: {command.entity_id}")
            if self.event_bus: self.event_bus.publish(ChartDeletedEvent(command.entity_id, result, command.tenant_id))
            return CommandResult.ok({"deleted": True, "chart_id": command.entity_id})
        except Exception as e:
            logger.error(f"Error deleting chart: {e}")
            return CommandResult.error(f"Failed to delete chart: {str(e)}")


class GetChartHandler(QueryHandler):
    def __init__(self, repository: ChartRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "GetChart"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, GetChartCommand): return CommandResult.error(f"Invalid command type")
        if not command.entity_id: return CommandResult.error("Chart ID is required")
        result = self.repository.find_by_id(command.entity_id)
        if not result: return CommandResult.error(f"Chart not found: {command.entity_id}")
        return CommandResult.ok(result)


class ListChartsHandler(QueryHandler):
    def __init__(self, repository: ChartRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "ListCharts"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, ListChartsCommand): return CommandResult.error(f"Invalid command type")
        try:
            filters = command.filters or {}
            pagination = command.pagination or {}
            result = self.repository.find_all(project_id=filters.get("project_id", command.project_id),
                page=pagination.get("page", 1), per_page=pagination.get("per_page", 20))
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error listing charts: {e}")
            return CommandResult.error(f"Failed to list charts: {str(e)}")


class CreateChartLibraryHandler(CreateHandler):
    def __init__(self, repository: ChartLibraryRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "CreateChartLibrary"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, CreateChartLibraryCommand): return CommandResult.error(f"Invalid command type")
        try:
            result = self.repository.create(command.to_payload())
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error creating chart library: {e}")
            return CommandResult.error(f"Failed to create chart library: {str(e)}")


class GetDefaultLibraryHandler(QueryHandler):
    def __init__(self, repository: ChartLibraryRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "GetDefaultLibrary"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, GetDefaultLibraryCommand): return CommandResult.error(f"Invalid command type")
        result = self.repository.find_default()
        if not result: return CommandResult.ok({"library_name": "chartjs", "is_default": True, "is_active": True})
        return CommandResult.ok(result)


class GetChartLibraryHandler(QueryHandler):
    def __init__(self, repository: ChartLibraryRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "GetChartLibrary"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, GetChartLibraryCommand): return CommandResult.error(f"Invalid command type")
        if not command.entity_id: return CommandResult.error("Library ID is required")
        result = self.repository.find_by_id(command.entity_id)
        if not result: return CommandResult.error(f"Chart library not found: {command.entity_id}")
        return CommandResult.ok(result)


class ListChartLibrariesHandler(QueryHandler):
    def __init__(self, repository: ChartLibraryRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "ListChartLibraries"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, ListChartLibrariesCommand): return CommandResult.error(f"Invalid command type")
        try:
            result = self.repository.find_all(page=1, per_page=100)
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error listing chart libraries: {e}")
            return CommandResult.error(f"Failed to list chart libraries: {str(e)}")


class UpdateChartLibraryHandler(UpdateHandler):
    def __init__(self, repository: ChartLibraryRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "UpdateChartLibrary"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, UpdateChartLibraryCommand): return CommandResult.error(f"Invalid command type")
        if not command.entity_id: return CommandResult.error("Library ID is required")
        try:
            result = self.repository.update(command.entity_id, command.to_payload())
            if not result: return CommandResult.error(f"Chart library not found: {command.entity_id}")
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error updating chart library: {e}")
            return CommandResult.error(f"Failed to update chart library: {str(e)}")


class DeleteChartLibraryHandler(DeleteHandler):
    def __init__(self, repository: ChartLibraryRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "DeleteChartLibrary"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, DeleteChartLibraryCommand): return CommandResult.error(f"Invalid command type")
        if not command.entity_id: return CommandResult.error("Library ID is required")
        try:
            result = self.repository.delete(command.entity_id)
            if not result: return CommandResult.error(f"Chart library not found: {command.entity_id}")
            return CommandResult.ok({"deleted": True, "library_id": command.entity_id})
        except Exception as e:
            logger.error(f"Error deleting chart library: {e}")
            return CommandResult.error(f"Failed to delete chart library: {str(e)}")

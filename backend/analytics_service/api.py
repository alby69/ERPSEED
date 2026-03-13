"""
Analytics Service API - Main entry point for Analytics Service.
"""
import logging
from typing import Dict, Any, Optional
from backend.shared.handlers import CommandResult
from backend.analytics_service.application.commands import (CreateChartCommand, UpdateChartCommand, DeleteChartCommand,
    GetChartCommand, ListChartsCommand, CreateChartLibraryCommand, GetDefaultLibraryCommand,
    GetChartLibraryCommand, ListChartLibrariesCommand, UpdateChartLibraryCommand, DeleteChartLibraryCommand)
from backend.analytics_service.application.handlers import (CreateChartHandler, UpdateChartHandler, DeleteChartHandler,
    GetChartHandler, ListChartsHandler, CreateChartLibraryHandler, GetDefaultLibraryHandler,
    GetChartLibraryHandler, ListChartLibrariesHandler, UpdateChartLibraryHandler, DeleteChartLibraryHandler)
from backend.analytics_service.infrastructure.repository import ChartRepository, ChartLibraryRepository
from backend.shared.events.event_bus import EventBus

logger = logging.getLogger(__name__)


class AnalyticsService:
    COMMAND_HANDLERS = {"CreateChart": CreateChartHandler, "UpdateChart": UpdateChartHandler, "DeleteChart": DeleteChartHandler,
        "GetChart": GetChartHandler, "ListCharts": ListChartsHandler, "CreateChartLibrary": CreateChartLibraryHandler,
        "GetDefaultLibrary": GetDefaultLibraryHandler, "GetChartLibrary": GetChartLibraryHandler,
        "ListChartLibraries": ListChartLibrariesHandler, "UpdateChartLibrary": UpdateChartLibraryHandler,
        "DeleteChartLibrary": DeleteChartLibraryHandler}
    
    def __init__(self, chart_repository: ChartRepository = None, library_repository: ChartLibraryRepository = None, event_bus: EventBus = None):
        self._chart_repository = chart_repository
        self._library_repository = library_repository
        self._event_bus = event_bus
        self._handlers = {}
    
    @property
    def chart_repository(self) -> ChartRepository:
        if self._chart_repository is None:
            from backend.extensions import db
            self._chart_repository = ChartRepository(db)
        return self._chart_repository
    
    @property
    def library_repository(self) -> ChartLibraryRepository:
        if self._library_repository is None:
            from backend.extensions import db
            self._library_repository = ChartLibraryRepository(db)
        return self._library_repository
    
    @property
    def event_bus(self) -> Optional[EventBus]:
        if self._event_bus is None:
            try: self._event_bus = EventBus()
            except Exception as e: logger.warning(f"Could not initialize EventBus: {e}")
        return self._event_bus
    
    def _get_handler(self, command_name: str):
        if command_name not in self._handlers:
            handler_class = self.COMMAND_HANDLERS.get(command_name)
            if not handler_class: return None
            if "Chart" in command_name and "Library" not in command_name:
                repo = self.chart_repository
            else:
                repo = self.library_repository
            self._handlers[command_name] = handler_class(repository=repo, event_bus=self.event_bus)
        return self._handlers[command_name]
    
    def execute(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        command_name = command_data.get("command")
        if not command_name: return CommandResult.error("Command name is required").to_dict()
        handler = self._get_handler(command_name)
        if not handler: return CommandResult.error(f"Unknown command: {command_name}").to_dict()
        command = self._parse_command(command_name, command_data)
        if isinstance(command, CommandResult): return command.to_dict()
        try:
            result = handler.handle(command)
            return result.to_dict()
        except Exception as e:
            logger.error(f"Error executing command {command_name}: {e}", exc_info=True)
            return CommandResult.error(f"Internal error: {str(e)}").to_dict()
    
    def _parse_command(self, command_name: str, data: Dict[str, Any]):
        command_classes = {"CreateChart": CreateChartCommand, "UpdateChart": UpdateChartCommand, "DeleteChart": DeleteChartCommand,
            "GetChart": GetChartCommand, "ListCharts": ListChartsCommand, "CreateChartLibrary": CreateChartLibraryCommand,
            "GetDefaultLibrary": GetDefaultLibraryCommand, "GetChartLibrary": GetChartLibraryCommand,
            "ListChartLibraries": ListChartLibrariesCommand, "UpdateChartLibrary": UpdateChartLibraryCommand,
            "DeleteChartLibrary": DeleteChartLibraryCommand}
        command_class = command_classes.get(command_name)
        if not command_class: return CommandResult.error(f"Unknown command: {command_name}")
        try:
            cmd = command_class.from_dict(data)
            cmd.entity_id = data.get("entity_id", data.get("id", 0))
            return cmd
        except Exception as e:
            logger.error(f"Error parsing command {command_name}: {e}")
            return CommandResult.error(f"Invalid command data: {str(e)}")
    
    def health_check(self) -> Dict[str, Any]:
        try: return {"status": "healthy", "service": "analytics_service", "version": "1.0.0"}
        except Exception as e: return {"status": "unhealthy", "service": "analytics_service", "error": str(e)}


_service_instance = None


def get_analytics_service() -> AnalyticsService:
    global _service_instance
    if _service_instance is None: _service_instance = AnalyticsService()
    return _service_instance


def execute(command_data: Dict[str, Any]) -> Dict[str, Any]:
    service = get_analytics_service()
    return service.execute(command_data)

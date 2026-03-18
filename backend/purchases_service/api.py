"""
Purchases Service API - Main entry point for Purchases Service.
"""
import logging
from typing import Dict, Any, Optional
from backend.shared.handlers import CommandResult
from backend.purchases_service.application.commands import (CreatePurchaseOrderCommand, UpdatePurchaseOrderCommand,
    DeletePurchaseOrderCommand, ConfirmPurchaseOrderCommand, ReceivePurchaseOrderCommand, CancelPurchaseOrderCommand,
    GetPurchaseOrderCommand, ListPurchaseOrdersCommand)
from backend.purchases_service.application.handlers import (CreatePurchaseOrderHandler, UpdatePurchaseOrderHandler,
    DeletePurchaseOrderHandler, ConfirmPurchaseOrderHandler, ReceivePurchaseOrderHandler, CancelPurchaseOrderHandler,
    GetPurchaseOrderHandler, ListPurchaseOrdersHandler)
from backend.purchases_service.infrastructure.repository import PurchaseOrderRepository
from backend.shared.events.event_bus import EventBus

logger = logging.getLogger(__name__)


class PurchaseService:
    COMMAND_HANDLERS = {"CreatePurchaseOrder": CreatePurchaseOrderHandler, "UpdatePurchaseOrder": UpdatePurchaseOrderHandler,
        "DeletePurchaseOrder": DeletePurchaseOrderHandler, "ConfirmPurchaseOrder": ConfirmPurchaseOrderHandler,
        "ReceivePurchaseOrder": ReceivePurchaseOrderHandler, "CancelPurchaseOrder": CancelPurchaseOrderHandler,
        "GetPurchaseOrder": GetPurchaseOrderHandler, "ListPurchaseOrders": ListPurchaseOrdersHandler}
    
    def __init__(self, repository: PurchaseOrderRepository = None, event_bus: EventBus = None):
        self._repository = repository
        self._event_bus = event_bus
        self._handlers = {}
    
    @property
    def repository(self) -> PurchaseOrderRepository:
        if self._repository is None:
            from backend.extensions import db
            self._repository = PurchaseOrderRepository(db)
        return self._repository
    
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
            self._handlers[command_name] = handler_class(repository=self.repository, event_bus=self.event_bus)
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
        command_classes = {"CreatePurchaseOrder": CreatePurchaseOrderCommand, "UpdatePurchaseOrder": UpdatePurchaseOrderCommand,
            "DeletePurchaseOrder": DeletePurchaseOrderCommand, "ConfirmPurchaseOrder": ConfirmPurchaseOrderCommand,
            "ReceivePurchaseOrder": ReceivePurchaseOrderCommand, "CancelPurchaseOrder": CancelPurchaseOrderCommand,
            "GetPurchaseOrder": GetPurchaseOrderCommand, "ListPurchaseOrders": ListPurchaseOrdersCommand}
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
        try: return {"status": "healthy", "service": "purchases_service", "version": "1.0.0"}
        except Exception as e: return {"status": "unhealthy", "service": "purchases_service", "error": str(e)}


_service_instance = None


def get_purchase_service() -> PurchaseService:
    global _service_instance
    if _service_instance is None: _service_instance = PurchaseService()
    return _service_instance


def execute(command_data: Dict[str, Any]) -> Dict[str, Any]:
    service = get_purchase_service()
    return service.execute(command_data)

"""
Purchases Command Handlers - Handle commands and return results.
"""
import logging
from backend.shared.handlers import CommandHandler, CommandResult, CreateHandler, UpdateHandler, DeleteHandler, QueryHandler
from backend.shared.commands import Command
from backend.purchases_service.application.commands import (CreatePurchaseOrderCommand, UpdatePurchaseOrderCommand,
    DeletePurchaseOrderCommand, ConfirmPurchaseOrderCommand, ReceivePurchaseOrderCommand, CancelPurchaseOrderCommand,
    GetPurchaseOrderCommand, ListPurchaseOrdersCommand)
from backend.purchases_service.domain.events import (PurchaseOrderCreatedEvent, PurchaseOrderUpdatedEvent,
    PurchaseOrderConfirmedEvent, PurchaseOrderReceivedEvent, PurchaseOrderCancelledEvent)
from backend.purchases_service.infrastructure.repository import PurchaseOrderRepository
from backend.entities.soggetto import Soggetto

logger = logging.getLogger(__name__)


class CreatePurchaseOrderHandler(CreateHandler):
    def __init__(self, repository: PurchaseOrderRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "CreatePurchaseOrder"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, CreatePurchaseOrderCommand):
            return CommandResult.error(f"Invalid command type: {type(command)}")
        
        supplier = Soggetto.query.filter_by(id=command.supplier_id, tenant_id=command.tenant_id).first()
        if not supplier: return CommandResult.error("Supplier not found")
        
        try:
            result = self.repository.create({**command.to_payload(), "tenant_id": command.tenant_id})
            if self.event_bus:
                self.event_bus.publish(PurchaseOrderCreatedEvent(result["id"], result, command.tenant_id))
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error creating purchase order: {e}")
            return CommandResult.error(f"Failed to create order: {str(e)}")


class UpdatePurchaseOrderHandler(UpdateHandler):
    def __init__(self, repository: PurchaseOrderRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "UpdatePurchaseOrder"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, UpdatePurchaseOrderCommand): return CommandResult.error(f"Invalid command type")
        if not command.entity_id: return CommandResult.error("Order ID is required")
        existing = self.repository.find_by_id(command.entity_id, command.tenant_id)
        if not existing: return CommandResult.error(f"Order not found: {command.entity_id}")
        try:
            result = self.repository.update(command.entity_id, command.tenant_id, command.to_payload())
            if self.event_bus and result:
                self.event_bus.publish(PurchaseOrderUpdatedEvent(command.entity_id, result["old"], result["new"], command.tenant_id))
            return CommandResult.ok(result["new"])
        except Exception as e:
            logger.error(f"Error updating purchase order: {e}")
            return CommandResult.error(f"Failed to update order: {str(e)}")


class DeletePurchaseOrderHandler(DeleteHandler):
    def __init__(self, repository: PurchaseOrderRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "DeletePurchaseOrder"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, DeletePurchaseOrderCommand): return CommandResult.error(f"Invalid command type")
        if not command.entity_id: return CommandResult.error("Order ID is required")
        check = self.repository.check_can_delete(command.entity_id, command.tenant_id)
        if not check["can_delete"]: return CommandResult.error(check["reason"])
        try:
            result = self.repository.delete(command.entity_id, command.tenant_id)
            return CommandResult.ok({"deleted": True, "order_id": command.entity_id})
        except Exception as e:
            logger.error(f"Error deleting purchase order: {e}")
            return CommandResult.error(f"Failed to delete order: {str(e)}")


class ConfirmPurchaseOrderHandler(CommandHandler):
    def __init__(self, repository: PurchaseOrderRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "ConfirmPurchaseOrder"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, ConfirmPurchaseOrderCommand): return CommandResult.error(f"Invalid command type")
        existing = self.repository.find_by_id(command.entity_id, command.tenant_id)
        if not existing: return CommandResult.error(f"Order not found: {command.entity_id}")
        if existing["status"] != "draft": return CommandResult.error("Only draft orders can be confirmed")
        try:
            result = self.repository.confirm(command.entity_id, command.tenant_id)
            if self.event_bus and result:
                self.event_bus.publish(PurchaseOrderConfirmedEvent(command.entity_id, result, command.tenant_id))
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error confirming purchase order: {e}")
            return CommandResult.error(f"Failed to confirm order: {str(e)}")


class ReceivePurchaseOrderHandler(CommandHandler):
    def __init__(self, repository: PurchaseOrderRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "ReceivePurchaseOrder"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, ReceivePurchaseOrderCommand): return CommandResult.error(f"Invalid command type")
        existing = self.repository.find_by_id(command.entity_id, command.tenant_id)
        if not existing: return CommandResult.error(f"Order not found: {command.entity_id}")
        if existing["status"] != "confirmed": return CommandResult.error("Only confirmed orders can be received")
        try:
            result = self.repository.receive(command.entity_id, command.tenant_id)
            if self.event_bus and result:
                self.event_bus.publish(PurchaseOrderReceivedEvent(command.entity_id, result, command.tenant_id))
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error receiving purchase order: {e}")
            return CommandResult.error(f"Failed to receive order: {str(e)}")


class CancelPurchaseOrderHandler(CommandHandler):
    def __init__(self, repository: PurchaseOrderRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    
    @property
    def command_type(self) -> str: return "CancelPurchaseOrder"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, CancelPurchaseOrderCommand): return CommandResult.error(f"Invalid command type")
        existing = self.repository.find_by_id(command.entity_id, command.tenant_id)
        if not existing: return CommandResult.error(f"Order not found: {command.entity_id}")
        if existing["status"] in ["received", "cancelled"]: return CommandResult.error("Order cannot be cancelled in current status")
        try:
            result = self.repository.cancel(command.entity_id, command.tenant_id)
            if self.event_bus and result:
                self.event_bus.publish(PurchaseOrderCancelledEvent(command.entity_id, result, command.tenant_id))
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error cancelling purchase order: {e}")
            return CommandResult.error(f"Failed to cancel order: {str(e)}")


class GetPurchaseOrderHandler(QueryHandler):
    def __init__(self, repository: PurchaseOrderRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    @property
    def command_type(self) -> str: return "GetPurchaseOrder"


class ListPurchaseOrdersHandler(QueryHandler):
    def __init__(self, repository: PurchaseOrderRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus
    @property
    def command_type(self) -> str: return "GetPurchaseOrder"
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, GetPurchaseOrderCommand): return CommandResult.error(f"Invalid command type")
        if not command.entity_id: return CommandResult.error("Order ID is required")
        result = self.repository.find_by_id(command.entity_id, command.tenant_id)
        if not result: return CommandResult.error(f"Order not found: {command.entity_id}")
        return CommandResult.ok(result)


class ListPurchaseOrdersHandler(QueryHandler):
    def __init__(self, repository: PurchaseOrderRepository): self.repository = repository
    @property
    def command_type(self) -> str: return "ListPurchaseOrders"
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, ListPurchaseOrdersCommand): return CommandResult.error(f"Invalid command type")
        try:
            filters = command.filters or {}
            pagination = command.pagination or {}
            result = self.repository.find_all(command.tenant_id,
                search=filters.get("search", command.search), status=filters.get("status", command.status),
                supplier_id=filters.get("supplier_id", command.supplier_id),
                page=pagination.get("page", 1), per_page=pagination.get("per_page", 20),
                sort_by=pagination.get("sort_by", "date"), sort_order=pagination.get("sort_order", "desc"))
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error listing purchase orders: {e}")
            return CommandResult.error(f"Failed to list orders: {str(e)}")

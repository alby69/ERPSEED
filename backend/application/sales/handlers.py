"""
Sales Handlers - Handle commands and return results.
"""
import logging
from backend.shared.handlers import CommandHandler, CommandResult, CreateHandler, UpdateHandler, DeleteHandler, QueryHandler
from backend.shared.commands import Command

from backend.application.sales.commands import (
    CreateSalesOrderCommand, UpdateSalesOrderCommand, DeleteSalesOrderCommand,
    ConfirmSalesOrderCommand, CancelSalesOrderCommand, GetSalesOrderCommand, ListSalesOrdersCommand,
)
from backend.domain.sales import (
    SalesOrderCreatedEvent, SalesOrderUpdatedEvent, SalesOrderConfirmedEvent,
    SalesOrderCancelledEvent, SalesOrderDeletedEvent,
)
from backend.infrastructure.sales.repository import SalesOrderRepository
from backend.infrastructure.entities.models import Soggetto

logger = logging.getLogger(__name__)


class CreateSalesOrderHandler(CreateHandler):
    def __init__(self, repository: SalesOrderRepository, event_bus=None):
        self.repository = repository; self.event_bus = event_bus

    @property
    def command_type(self) -> str: return "CreateSalesOrder"

    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, CreateSalesOrderCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        customer = Soggetto.query.filter_by(id=command.customer_id, tenant_id=command.tenant_id).first()
        if not customer: return CommandResult.error("Customer not found")
        try:
            result = self.repository.create({**command.to_payload(), "tenant_id": command.tenant_id})
            if self.event_bus: self.event_bus.publish(SalesOrderCreatedEvent(result["id"], result, command.tenant_id))
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error creating sales order: {e}")
            return CommandResult.error(f"Failed to create order: {str(e)}")


class UpdateSalesOrderHandler(UpdateHandler):
    def __init__(self, repository: SalesOrderRepository, event_bus=None):
        self.repository = repository; self.event_bus = event_bus

    @property
    def command_type(self) -> str: return "UpdateSalesOrder"

    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, UpdateSalesOrderCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        if not command.entity_id: return CommandResult.error("Order ID is required")
        existing = self.repository.find_by_id(command.entity_id, command.tenant_id)
        if not existing: return CommandResult.error(f"Order not found: {command.entity_id}")
        try:
            result = self.repository.update(command.entity_id, command.tenant_id, command.to_payload())
            if self.event_bus and result: self.event_bus.publish(SalesOrderUpdatedEvent(command.entity_id, result["old"], result["new"], command.tenant_id))
            return CommandResult.ok(result["new"])
        except Exception as e:
            logger.error(f"Error updating sales order: {e}")
            return CommandResult.error(f"Failed to update order: {str(e)}")


class DeleteSalesOrderHandler(DeleteHandler):
    def __init__(self, repository: SalesOrderRepository, event_bus=None):
        self.repository = repository; self.event_bus = event_bus

    @property
    def command_type(self) -> str: return "DeleteSalesOrder"

    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, DeleteSalesOrderCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        if not command.entity_id: return CommandResult.error("Order ID is required")
        check = self.repository.check_can_delete(command.entity_id, command.tenant_id)
        if not check["can_delete"]: return CommandResult.error(check["reason"])
        try:
            result = self.repository.delete(command.entity_id, command.tenant_id)
            if self.event_bus and result: self.event_bus.publish(SalesOrderDeletedEvent(command.entity_id, result, command.tenant_id))
            return CommandResult.ok({"deleted": True, "order_id": command.entity_id})
        except Exception as e:
            logger.error(f"Error deleting sales order: {e}")
            return CommandResult.error(f"Failed to delete order: {str(e)}")


class ConfirmSalesOrderHandler(CommandHandler):
    def __init__(self, repository: SalesOrderRepository, event_bus=None):
        self.repository = repository; self.event_bus = event_bus

    @property
    def command_type(self) -> str: return "ConfirmSalesOrder"

    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, ConfirmSalesOrderCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        existing = self.repository.find_by_id(command.entity_id, command.tenant_id)
        if not existing: return CommandResult.error(f"Order not found: {command.entity_id}")
        if existing["status"] != "draft": return CommandResult.error("Only draft orders can be confirmed")
        try:
            result = self.repository.confirm(command.entity_id, command.tenant_id)
            if self.event_bus and result: self.event_bus.publish(SalesOrderConfirmedEvent(command.entity_id, result, command.tenant_id))
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error confirming sales order: {e}")
            return CommandResult.error(f"Failed to confirm order: {str(e)}")


class CancelSalesOrderHandler(CommandHandler):
    def __init__(self, repository: SalesOrderRepository, event_bus=None):
        self.repository = repository; self.event_bus = event_bus

    @property
    def command_type(self) -> str: return "CancelSalesOrder"

    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, CancelSalesOrderCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        existing = self.repository.find_by_id(command.entity_id, command.tenant_id)
        if not existing: return CommandResult.error(f"Order not found: {command.entity_id}")
        if existing["status"] in ["completed", "cancelled"]: return CommandResult.error("Order cannot be cancelled in current status")
        try:
            result = self.repository.cancel(command.entity_id, command.tenant_id)
            if self.event_bus and result: self.event_bus.publish(SalesOrderCancelledEvent(command.entity_id, result, command.tenant_id))
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error cancelling sales order: {e}")
            return CommandResult.error(f"Failed to cancel order: {str(e)}")


class GetSalesOrderHandler(QueryHandler):
    def __init__(self, repository: SalesOrderRepository, event_bus=None):
        self.repository = repository; self.event_bus = event_bus

    @property
    def command_type(self) -> str: return "GetSalesOrder"

    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, GetSalesOrderCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        if not command.entity_id: return CommandResult.error("Order ID is required")
        result = self.repository.find_by_id(command.entity_id, command.tenant_id)
        if not result: return CommandResult.error(f"Order not found: {command.entity_id}")
        return CommandResult.ok(result)


class ListSalesOrdersHandler(QueryHandler):
    def __init__(self, repository: SalesOrderRepository, event_bus=None):
        self.repository = repository; self.event_bus = event_bus

    @property
    def command_type(self) -> str: return "ListSalesOrders"

    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, ListSalesOrdersCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        try:
            filters = command.filters or {}; pagination = command.pagination or {}
            result = self.repository.find_all(tenant_id=command.tenant_id,
                search=filters.get("search", command.search), status=filters.get("status", command.status),
                customer_id=filters.get("customer_id", command.customer_id),
                page=pagination.get("page", 1), per_page=pagination.get("per_page", 20),
                sort_by=pagination.get("sort_by", "date"), sort_order=pagination.get("sort_order", "desc"))
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error listing sales orders: {e}")
            return CommandResult.error(f"Failed to list orders: {str(e)}")

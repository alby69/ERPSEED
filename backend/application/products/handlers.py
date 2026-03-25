"""
Product Application Handlers.

Handle commands and return results. Stateless and testable.
"""
import logging
from typing import Optional

from backend.shared.handlers import CommandHandler, CommandResult, CreateHandler, UpdateHandler, DeleteHandler, QueryHandler
from backend.shared.commands import Command

from backend.application.products.commands import (
    CreateProductCommand, UpdateProductCommand, DeleteProductCommand,
    ListProductsCommand, GetProductCommand, UpdateStockCommand,
)
from backend.domain.products import Product, ProductCreatedEvent, ProductUpdatedEvent, ProductDeletedEvent
from backend.domain.products import ProductStockChangedEvent, ProductLowStockEvent
from backend.infrastructure.products.repository import ProductRepository

logger = logging.getLogger(__name__)


class CreateProductHandler(CreateHandler):
    def __init__(self, repository: ProductRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus

    @property
    def command_type(self) -> str: return "CreateProduct"

    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, CreateProductCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        product = Product.from_dict(command.to_payload())
        product.tenant_id = command.tenant_id
        is_valid, errors = product.validate()
        if not is_valid: return CommandResult.error("Validation failed", errors)
        existing = self.repository.find_by_code(product.code, command.tenant_id)
        if existing: return CommandResult.error(f"Product with code '{product.code}' already exists")
        try:
            result = self.repository.create(product.to_dict())
            if self.event_bus: self.event_bus.publish(ProductCreatedEvent(result["id"], result, command.tenant_id))
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error creating product: {e}")
            return CommandResult.error(f"Failed to create product: {str(e)}")


class UpdateProductHandler(UpdateHandler):
    def __init__(self, repository: ProductRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus

    @property
    def command_type(self) -> str: return "UpdateProduct"

    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, UpdateProductCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        if not command.entity_id: return CommandResult.error("Product ID is required")
        existing = self.repository.find_by_id(command.entity_id, command.tenant_id)
        if not existing: return CommandResult.error(f"Product not found: {command.entity_id}")
        if command.code and command.code != existing["code"]:
            duplicate = self.repository.find_by_code(command.code, command.tenant_id)
            if duplicate: return CommandResult.error(f"Product with code '{command.code}' already exists")
        try:
            result = self.repository.update(command.entity_id, command.tenant_id, command.to_payload())
            if self.event_bus and result:
                self.event_bus.publish(ProductUpdatedEvent(command.entity_id, result["old"], result["new"], command.tenant_id))
            return CommandResult.ok(result["new"] if result else None)
        except Exception as e:
            logger.error(f"Error updating product: {e}")
            return CommandResult.error(f"Failed to update product: {str(e)}")


class DeleteProductHandler(DeleteHandler):
    def __init__(self, repository: ProductRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus

    @property
    def command_type(self) -> str: return "DeleteProduct"

    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, DeleteProductCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        if not command.entity_id: return CommandResult.error("Product ID is required")
        existing = self.repository.find_by_id(command.entity_id, command.tenant_id)
        if not existing: return CommandResult.error(f"Product not found: {command.entity_id}")
        deps = self.repository.check_dependencies(command.entity_id, command.tenant_id)
        if deps.get("has_dependencies"):
            return CommandResult.error("Cannot delete product with associated orders or stock records. Consider deactivating it instead.")
        try:
            result = self.repository.delete(command.entity_id, command.tenant_id)
            if self.event_bus: self.event_bus.publish(ProductDeletedEvent(command.entity_id, result, command.tenant_id))
            return CommandResult.ok({"deleted": True, "product_id": command.entity_id})
        except Exception as e:
            logger.error(f"Error deleting product: {e}")
            return CommandResult.error(f"Failed to delete product: {str(e)}")


class GetProductHandler(QueryHandler):
    def __init__(self, repository: ProductRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus

    @property
    def command_type(self) -> str: return "GetProduct"

    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, GetProductCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        if not command.entity_id: return CommandResult.error("Product ID is required")
        result = self.repository.find_by_id(command.entity_id, command.tenant_id)
        if not result: return CommandResult.error(f"Product not found: {command.entity_id}")
        return CommandResult.ok(result)


class ListProductsHandler(QueryHandler):
    def __init__(self, repository: ProductRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus

    @property
    def command_type(self) -> str: return "ListProducts"

    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, ListProductsCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        try:
            filters = command.filters or {}
            pagination = command.pagination or {}
            result = self.repository.find_all(
                tenant_id=command.tenant_id,
                search=filters.get("search", command.search),
                category=filters.get("category", command.category),
                is_active=filters.get("is_active", command.is_active),
                min_price=filters.get("min_price", command.min_price),
                max_price=filters.get("max_price", command.max_price),
                page=pagination.get("page", 1),
                per_page=pagination.get("per_page", 20),
                sort_by=pagination.get("sort_by", "name"),
                sort_order=pagination.get("sort_order", "asc"),
            )
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error listing products: {e}")
            return CommandResult.error(f"Failed to list products: {str(e)}")


class UpdateStockHandler(CommandHandler):
    def __init__(self, repository: ProductRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus

    @property
    def command_type(self) -> str: return "UpdateStock"

    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, UpdateStockCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        if not command.product_id: return CommandResult.error("Product ID is required")
        existing = self.repository.find_by_id(command.product_id, command.tenant_id)
        if not existing: return CommandResult.error(f"Product not found: {command.product_id}")
        if not existing.get("track_inventory"): return CommandResult.error("Product does not track inventory")
        try:
            old_stock = existing["current_stock"]
            result = self.repository.update(command.product_id, command.tenant_id, {"current_stock": command.new_stock})
            if self.event_bus and result:
                new_stock = result["new"]["current_stock"]
                self.event_bus.publish(ProductStockChangedEvent(command.product_id, old_stock, new_stock, command.reason, command.tenant_id))
                if new_stock <= existing.get("reorder_level", 0):
                    self.event_bus.publish(ProductLowStockEvent(command.product_id, new_stock, existing.get("reorder_level", 0), command.tenant_id))
            return CommandResult.ok(result["new"] if result else None)
        except Exception as e:
            logger.error(f"Error updating stock: {e}")
            return CommandResult.error(f"Failed to update stock: {str(e)}")

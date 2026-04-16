"""
Products Service API - Main entry point for Products Service.

This module provides a unified interface to handle all product-related operations.
It receives JSON commands and returns JSON results, making it:
- Testable via CLI
- Usable from any frontend
- Easily integrable with other services
"""
import logging
from typing import Dict, Any, Optional

from shared.handlers import CommandResult

from modules.products.application.commands import (
    CreateProductCommand,
    UpdateProductCommand,
    DeleteProductCommand,
    ListProductsCommand,
    GetProductCommand,
    UpdateStockCommand,
)
from modules.products.application.handlers import (
    CreateProductHandler,
    UpdateProductHandler,
    DeleteProductHandler,
    GetProductHandler,
    ListProductsHandler,
    UpdateStockHandler,
)
from modules.products.infrastructure.repository import ProductRepository
from shared.events.event_bus import EventBus

logger = logging.getLogger(__name__)


class ProductService:
    """
    Main service class for Products.

    Usage:
        service = ProductService()

        # Create product
        result = service.execute({
            "command": "CreateProduct",
            "tenant_id": 1,
            "user_id": 1,
            "name": "My Product",
            "code": "PROD-001",
            "unit_price": 100.00
        })

        # List products
        result = service.execute({
            "command": "ListProducts",
            "tenant_id": 1,
            "pagination": {"page": 1, "per_page": 20}
        })
    """

    COMMAND_HANDLERS = {
        "CreateProduct": CreateProductHandler,
        "UpdateProduct": UpdateProductHandler,
        "DeleteProduct": DeleteProductHandler,
        "GetProduct": GetProductHandler,
        "ListProducts": ListProductsHandler,
        "UpdateStock": UpdateStockHandler,
    }

    def __init__(self, repository: ProductRepository = None, event_bus: EventBus = None):
        """
        Initialize the service.

        Args:
            repository: ProductRepository instance. If None, creates a new one.
            event_bus: EventBus instance. If None, uses global event bus.
        """
        self._repository = repository
        self._event_bus = event_bus
        self._handlers = {}

    @property
    def repository(self) -> ProductRepository:
        """Lazy-load repository."""
        if self._repository is None:
            from extensions import db
            self._repository = ProductRepository(db)
        return self._repository

    @property
    def event_bus(self) -> Optional[EventBus]:
        """Lazy-load event bus."""
        if self._event_bus is None:
            try:
                self._event_bus = EventBus()
            except Exception as e:
                logger.warning(f"Could not initialize EventBus: {e}")
        return self._event_bus

    def _get_handler(self, command_name: str):
        """Get or create a handler for the command."""
        if command_name not in self._handlers:
            handler_class = self.COMMAND_HANDLERS.get(command_name)
            if not handler_class:
                return None
            self._handlers[command_name] = handler_class(
                repository=self.repository,
                event_bus=self.event_bus
            )
        return self._handlers[command_name]

    def execute(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a command and return the result.

        This is the main entry point for the service. It accepts a dictionary
        (JSON) and returns a dictionary (JSON).

        Args:
            command_data: Dictionary containing:
                - command: Command name (required)
                - tenant_id: Tenant ID (required for most commands)
                - user_id: User ID (optional)
                - Other fields specific to the command

        Returns:
            Dictionary containing:
                - success: Boolean indicating success
                - data: Result data (if success)
                - error: Error message (if failure)
                - errors: List of validation errors (if failure)
                - metadata: Additional metadata
        """
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
            logger.error(f"Error executing command {command_name}: {e}", exc_info=True)
            return CommandResult.error(f"Internal error: {str(e)}").to_dict()

    def _parse_command(self, command_name: str, data: Dict[str, Any]):
        """Parse command data into command object."""
        command_classes = {
            "CreateProduct": CreateProductCommand,
            "UpdateProduct": UpdateProductCommand,
            "DeleteProduct": DeleteProductCommand,
            "GetProduct": GetProductCommand,
            "ListProducts": ListProductsCommand,
            "UpdateStock": UpdateStockCommand,
        }

        command_class = command_classes.get(command_name)
        if not command_class:
            return CommandResult.error(f"Unknown command: {command_name}")

        try:
            return command_class.from_dict(data)
        except Exception as e:
            logger.error(f"Error parsing command {command_name}: {e}")
            return CommandResult.error(f"Invalid command data: {str(e)}")

    def health_check(self) -> Dict[str, Any]:
        """Check if service is healthy."""
        try:
            return {
                "status": "healthy",
                "service": "products_service",
                "version": "1.0.0",
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "products_service",
                "error": str(e),
            }


# Singleton instance for easy access
_service_instance = None

def get_product_service() -> ProductService:
    """Get or create the singleton ProductService instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = ProductService()
    return _service_instance


def execute(command_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to execute a command.

    Usage from CLI:
        python -c "
        import json
        from modules.products.service_api import execute
        result = execute({'command': 'ListProducts', 'tenant_id': 1})
        print(json.dumps(result, indent=2))
        "
    """
    service = get_product_service()
    return service.execute(command_data)

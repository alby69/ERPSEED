"""
Products API - REST API for Products Service.

This module provides Flask-Smorest Blueprint for Products operations:
- Products: CRUD for products, stock management
"""
import logging
from typing import Dict, Any
from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.shared.handlers import CommandResult
from backend.application.products.commands import (
    CreateProductCommand, UpdateProductCommand, DeleteProductCommand,
    GetProductCommand, ListProductsCommand, UpdateStockCommand,
)
from backend.application.products.handlers import (
    CreateProductHandler, UpdateProductHandler, DeleteProductHandler,
    GetProductHandler, ListProductsHandler, UpdateStockHandler,
)
from backend.infrastructure.products.repository import ProductRepository

logger = logging.getLogger(__name__)

blp = Blueprint("products", __name__, url_prefix="/api/v1/products", description="Products Service API")


class ProductCommandExecutor:
    """Executes CQRS commands for Products service."""
    
    COMMAND_HANDLERS = {
        "CreateProduct": CreateProductHandler,
        "UpdateProduct": UpdateProductHandler,
        "DeleteProduct": DeleteProductHandler,
        "GetProduct": GetProductHandler,
        "ListProducts": ListProductsHandler,
        "UpdateStock": UpdateStockHandler,
    }
    
    def __init__(self):
        self._handlers = {}
        self._repository = None
        self._db = None
    
    @property
    def repository(self):
        if self._repository is None:
            from backend.extensions import db
            self._db = db
            self._repository = ProductRepository(db=self._db)
        return self._repository
    
    def _get_handler(self, command_name: str):
        if command_name not in self._handlers:
            handler_class = self.COMMAND_HANDLERS.get(command_name)
            if not handler_class:
                return None
            self._handlers[command_name] = handler_class(repository=self.repository)
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
            logger.error(f"Error executing command {command_name}: {e}", exc_info=True)
            return CommandResult.error(f"Internal error: {str(e)}").to_dict()
    
    def _parse_command(self, command_name: str, data: Dict[str, Any]):
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
            cmd = command_class.from_dict(data)
            cmd.entity_id = data.get("entity_id", data.get("id", 0))
            cmd.tenant_id = data.get("tenant_id", 1)
            cmd.user_id = data.get("user_id")
            return cmd
        except Exception as e:
            logger.error(f"Error parsing command {command_name}: {e}")
            return CommandResult.error(f"Invalid command data: {str(e)}")


_executor = ProductCommandExecutor()


def get_service():
    """Get the product command executor instance."""
    return _executor


@blp.route("")
class ProductList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """List all products."""
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        user_id = get_jwt_identity()
        
        result = get_service().execute({
            "command": "ListProducts",
            "tenant_id": tenant_id,
            "user_id": user_id,
            "pagination": {
                "page": request.args.get('page', 1, type=int),
                "per_page": request.args.get('per_page', 20, type=int)
            }
        })
        
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to list products"))
        
        return result.get("data", {})

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        """Create a new product."""
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        user_id = get_jwt_identity()
        data = request.get_json()
        
        result = get_service().execute({
            "command": "CreateProduct",
            "tenant_id": tenant_id,
            "user_id": user_id,
            **data
        })
        
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to create product"))
        
        return result.get("data", {}), 201


@blp.route("/<int:product_id>")
class ProductDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, product_id):
        """Get a product by ID."""
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        user_id = get_jwt_identity()
        
        result = get_service().execute({
            "command": "GetProduct",
            "tenant_id": tenant_id,
            "user_id": user_id,
            "entity_id": product_id
        })
        
        if not result.get("success"):
            abort(404, message=result.get("error", "Product not found"))
        
        return result.get("data", {})

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, product_id):
        """Update a product."""
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        user_id = get_jwt_identity()
        data = request.get_json()
        
        result = get_service().execute({
            "command": "UpdateProduct",
            "tenant_id": tenant_id,
            "user_id": user_id,
            "entity_id": product_id,
            **data
        })
        
        if not result.get("success"):
            abort(404, message=result.get("error", "Product not found"))
        
        return result.get("data", {})

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, product_id):
        """Delete a product."""
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        user_id = get_jwt_identity()
        
        result = get_service().execute({
            "command": "DeleteProduct",
            "tenant_id": tenant_id,
            "user_id": user_id,
            "entity_id": product_id
        })
        
        if not result.get("success"):
            abort(404, message=result.get("error", "Product not found"))
        
        return {"message": "Product deleted"}, 204


@blp.route("/<int:product_id>/stock")
class ProductStock(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, product_id):
        """Update product stock."""
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        user_id = get_jwt_identity()
        data = request.get_json()
        
        result = get_service().execute({
            "command": "UpdateStock",
            "tenant_id": tenant_id,
            "user_id": user_id,
            "product_id": product_id,
            "new_stock": data.get("quantity", 0),
            "reason": data.get("reason", "Manual adjustment")
        })
        
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to update stock"))
        
        return result.get("data", {})

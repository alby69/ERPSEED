"""
Purchases API - REST API for Purchases Service.

This module provides Flask-Smorest Blueprint for Purchases operations:
- Purchase Orders: CRUD, confirm, receive, cancel
"""
import logging
from typing import Dict, Any
from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.shared.handlers import CommandResult
from backend.application.purchases.commands import (
    CreatePurchaseOrderCommand, UpdatePurchaseOrderCommand, DeletePurchaseOrderCommand,
    ConfirmPurchaseOrderCommand, ReceivePurchaseOrderCommand, CancelPurchaseOrderCommand,
    GetPurchaseOrderCommand, ListPurchaseOrdersCommand,
)
from backend.application.purchases.handlers import (
    CreatePurchaseOrderHandler, UpdatePurchaseOrderHandler, DeletePurchaseOrderHandler,
    ConfirmPurchaseOrderHandler, ReceivePurchaseOrderHandler, CancelPurchaseOrderHandler,
    GetPurchaseOrderHandler, ListPurchaseOrdersHandler,
)
from backend.infrastructure.purchases.repository import PurchaseOrderRepository

logger = logging.getLogger(__name__)

blp = Blueprint("purchases", __name__, url_prefix="/api/v1/purchases", description="Purchases Service API")


class PurchaseCommandExecutor:
    """Executes CQRS commands for Purchases service."""
    
    COMMAND_HANDLERS = {
        "CreatePurchaseOrder": CreatePurchaseOrderHandler,
        "UpdatePurchaseOrder": UpdatePurchaseOrderHandler,
        "DeletePurchaseOrder": DeletePurchaseOrderHandler,
        "ConfirmPurchaseOrder": ConfirmPurchaseOrderHandler,
        "ReceivePurchaseOrder": ReceivePurchaseOrderHandler,
        "CancelPurchaseOrder": CancelPurchaseOrderHandler,
        "GetPurchaseOrder": GetPurchaseOrderHandler,
        "ListPurchaseOrders": ListPurchaseOrdersHandler,
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
            self._repository = PurchaseOrderRepository(db=self._db)
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
            "CreatePurchaseOrder": CreatePurchaseOrderCommand,
            "UpdatePurchaseOrder": UpdatePurchaseOrderCommand,
            "DeletePurchaseOrder": DeletePurchaseOrderCommand,
            "ConfirmPurchaseOrder": ConfirmPurchaseOrderCommand,
            "ReceivePurchaseOrder": ReceivePurchaseOrderCommand,
            "CancelPurchaseOrder": CancelPurchaseOrderCommand,
            "GetPurchaseOrder": GetPurchaseOrderCommand,
            "ListPurchaseOrders": ListPurchaseOrdersCommand,
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


_executor = PurchaseCommandExecutor()


def get_service():
    """Get the purchases command executor instance."""
    return _executor


@blp.route("/orders")
class PurchaseOrderList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """List all purchase orders."""
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        user_id = get_jwt_identity()
        
        result = get_service().execute({
            "command": "ListPurchaseOrders",
            "tenant_id": tenant_id,
            "user_id": user_id,
            "pagination": {
                "page": request.args.get('page', 1, type=int),
                "per_page": request.args.get('per_page', 20, type=int)
            }
        })
        
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to list orders"))
        
        return result.get("data", {})

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        """Create a new purchase order."""
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        user_id = get_jwt_identity()
        data = request.get_json()
        
        result = get_service().execute({
            "command": "CreatePurchaseOrder",
            "tenant_id": tenant_id,
            "user_id": user_id,
            **data
        })
        
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to create order"))
        
        return result.get("data", {}), 201


@blp.route("/orders/<int:order_id>")
class PurchaseOrderDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, order_id):
        """Get a purchase order by ID."""
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        user_id = get_jwt_identity()
        
        result = get_service().execute({
            "command": "GetPurchaseOrder",
            "tenant_id": tenant_id,
            "user_id": user_id,
            "entity_id": order_id
        })
        
        if not result.get("success"):
            abort(404, message=result.get("error", "Order not found"))
        
        return result.get("data", {})

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, order_id):
        """Update a purchase order."""
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        user_id = get_jwt_identity()
        data = request.get_json()
        
        result = get_service().execute({
            "command": "UpdatePurchaseOrder",
            "tenant_id": tenant_id,
            "user_id": user_id,
            "entity_id": order_id,
            **data
        })
        
        if not result.get("success"):
            abort(404, message=result.get("error", "Order not found"))
        
        return result.get("data", {})

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, order_id):
        """Delete a purchase order."""
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        user_id = get_jwt_identity()
        
        result = get_service().execute({
            "command": "DeletePurchaseOrder",
            "tenant_id": tenant_id,
            "user_id": user_id,
            "entity_id": order_id
        })
        
        if not result.get("success"):
            abort(404, message=result.get("error", "Order not found"))
        
        return {"message": "Order deleted"}, 204


@blp.route("/orders/<int:order_id>/confirm")
class PurchaseOrderConfirm(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, order_id):
        """Confirm a purchase order."""
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        user_id = get_jwt_identity()
        
        result = get_service().execute({
            "command": "ConfirmPurchaseOrder",
            "tenant_id": tenant_id,
            "user_id": user_id,
            "entity_id": order_id
        })
        
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to confirm order"))
        
        return result.get("data", {})


@blp.route("/orders/<int:order_id>/receive")
class PurchaseOrderReceive(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, order_id):
        """Receive a purchase order."""
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        user_id = get_jwt_identity()
        
        result = get_service().execute({
            "command": "ReceivePurchaseOrder",
            "tenant_id": tenant_id,
            "user_id": user_id,
            "entity_id": order_id
        })
        
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to receive order"))
        
        return result.get("data", {})


@blp.route("/orders/<int:order_id>/cancel")
class PurchaseOrderCancel(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, order_id):
        """Cancel a purchase order."""
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        user_id = get_jwt_identity()
        
        result = get_service().execute({
            "command": "CancelPurchaseOrder",
            "tenant_id": tenant_id,
            "user_id": user_id,
            "entity_id": order_id
        })
        
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to cancel order"))
        
        return result.get("data", {})

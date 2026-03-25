"""
Sales API - REST API for Sales Service.

This module provides Flask-Smorest Blueprint for Sales operations:
- Sales Orders: CRUD, confirm, cancel
"""
import logging
from typing import Dict, Any
from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.shared.handlers import CommandResult
from backend.application.sales.commands import (
    CreateSalesOrderCommand, UpdateSalesOrderCommand, DeleteSalesOrderCommand,
    ConfirmSalesOrderCommand, CancelSalesOrderCommand, GetSalesOrderCommand, ListSalesOrdersCommand,
)
from backend.application.sales.handlers import (
    CreateSalesOrderHandler, UpdateSalesOrderHandler, DeleteSalesOrderHandler,
    ConfirmSalesOrderHandler, CancelSalesOrderHandler, GetSalesOrderHandler, ListSalesOrdersHandler,
)
from backend.infrastructure.sales.repository import SalesOrderRepository

def _get_tenant_id_from_jwt():
    from flask_jwt_extended import get_jwt
    try:
        claims = get_jwt()
        return claims.get('tenant_id', 1)
    except Exception:
        from backend.core.services.tenant_context import TenantContext
        tenant = TenantContext.get_tenant()
        return tenant.id if tenant else 1


logger = logging.getLogger(__name__)

blp = Blueprint("sales", __name__, url_prefix="/api/v1/sales", description="Sales Service API")


class SalesCommandExecutor:
    """Executes CQRS commands for Sales service."""

    COMMAND_HANDLERS = {
        "CreateSalesOrder": CreateSalesOrderHandler,
        "UpdateSalesOrder": UpdateSalesOrderHandler,
        "DeleteSalesOrder": DeleteSalesOrderHandler,
        "ConfirmSalesOrder": ConfirmSalesOrderHandler,
        "CancelSalesOrder": CancelSalesOrderHandler,
        "GetSalesOrder": GetSalesOrderHandler,
        "ListSalesOrders": ListSalesOrdersHandler,
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
            self._repository = SalesOrderRepository(db=self._db)
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
            "CreateSalesOrder": CreateSalesOrderCommand,
            "UpdateSalesOrder": UpdateSalesOrderCommand,
            "DeleteSalesOrder": DeleteSalesOrderCommand,
            "ConfirmSalesOrder": ConfirmSalesOrderCommand,
            "CancelSalesOrder": CancelSalesOrderCommand,
            "GetSalesOrder": GetSalesOrderCommand,
            "ListSalesOrders": ListSalesOrdersCommand,
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


_executor = SalesCommandExecutor()


def get_service():
    """Get the sales command executor instance."""
    return _executor


@blp.route("/orders")
class SalesOrderList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """List all sales orders."""
        tenant_id = _get_tenant_id_from_jwt()
        user_id = get_jwt_identity()

        result = get_service().execute({
            "command": "ListSalesOrders",
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
        """Create a new sales order."""
        tenant_id = _get_tenant_id_from_jwt()
        user_id = get_jwt_identity()
        data = request.get_json()

        result = get_service().execute({
            "command": "CreateSalesOrder",
            "tenant_id": tenant_id,
            "user_id": user_id,
            **data
        })

        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to create order"))

        return result.get("data", {}), 201


@blp.route("/orders/<int:order_id>")
class SalesOrderDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, order_id):
        """Get a sales order by ID."""
        tenant_id = _get_tenant_id_from_jwt()
        user_id = get_jwt_identity()

        result = get_service().execute({
            "command": "GetSalesOrder",
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
        """Update a sales order."""
        tenant_id = _get_tenant_id_from_jwt()
        user_id = get_jwt_identity()
        data = request.get_json()

        result = get_service().execute({
            "command": "UpdateSalesOrder",
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
        """Delete a sales order."""
        tenant_id = _get_tenant_id_from_jwt()
        user_id = get_jwt_identity()

        result = get_service().execute({
            "command": "DeleteSalesOrder",
            "tenant_id": tenant_id,
            "user_id": user_id,
            "entity_id": order_id
        })

        if not result.get("success"):
            abort(404, message=result.get("error", "Order not found"))

        return {"message": "Order deleted"}, 204


@blp.route("/orders/<int:order_id>/confirm")
class SalesOrderConfirm(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, order_id):
        """Confirm a sales order."""
        tenant_id = _get_tenant_id_from_jwt()
        user_id = get_jwt_identity()

        result = get_service().execute({
            "command": "ConfirmSalesOrder",
            "tenant_id": tenant_id,
            "user_id": user_id,
            "entity_id": order_id
        })

        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to confirm order"))

        return result.get("data", {})


@blp.route("/orders/<int:order_id>/cancel")
class SalesOrderCancel(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, order_id):
        """Cancel a sales order."""
        tenant_id = _get_tenant_id_from_jwt()
        user_id = get_jwt_identity()

        result = get_service().execute({
            "command": "CancelSalesOrder",
            "tenant_id": tenant_id,
            "user_id": user_id,
            "entity_id": order_id
        })

        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to cancel order"))

        return result.get("data", {})

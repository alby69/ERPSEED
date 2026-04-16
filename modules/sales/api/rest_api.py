"""
Sales Service REST API - Flask endpoints for Sales Service.

Provides REST API to access SalesService functionality.
"""

from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from modules.sales import get_sales_service

blp = Blueprint("sales_api", __name__, url_prefix="/api/v1/sales", description="Sales API")


def get_service():
    """Get the sales service instance."""
    return get_sales_service()


@blp.route("/orders")
class SalesOrderList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """List all sales orders."""
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
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
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
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
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
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
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
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
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
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
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
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
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
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

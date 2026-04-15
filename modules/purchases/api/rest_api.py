from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from extensions import db
from core.decorators.decorators import tenant_required
from core.schemas.schemas import PurchaseOrderSchema, BaseSchema
from modules.purchases import get_purchase_service

blp = Blueprint("purchases", __name__, description="Operations on purchase orders")


@blp.route("/purchases")
class PurchaseList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, PurchaseOrderSchema(many=True))
    def get(self, tenant_id):
        """List all purchase orders"""
        service = get_purchase_service()
        result = service.execute({
            "command": "ListPurchaseOrders",
            "tenant_id": tenant_id
        })

        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to list purchases"))

        return result["data"]["items"]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.arguments(PurchaseOrderSchema)
    @blp.response(201, PurchaseOrderSchema)
    def post(self, purchase_data, tenant_id):
        """Create a new purchase order"""
        service = get_purchase_service()

        payload = {}
        if hasattr(purchase_data, 'items'):
            for key, value in purchase_data.items():
                payload[key] = value
        else:
            payload = dict(purchase_data)

        result = service.execute({
            "command": "CreatePurchaseOrder",
            "tenant_id": tenant_id,
            **payload
        })

        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to create purchase"))

        return result["data"], 201


@blp.route("/purchases/<int:purchase_id>")
class PurchaseResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, PurchaseOrderSchema)
    def get(self, purchase_id, tenant_id):
        """Get purchase order by ID"""
        service = get_purchase_service()
        result = service.execute({
            "command": "GetPurchaseOrder",
            "tenant_id": tenant_id,
            "entity_id": purchase_id
        })

        if not result.get("success"):
            abort(404, message=result.get("error", "Purchase not found"))

        return result["data"]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.arguments(BaseSchema)
    @blp.response(200, PurchaseOrderSchema)
    def put(self, purchase_data, purchase_id, tenant_id):
        """Update a purchase order"""
        service = get_purchase_service()

        payload = {}
        if hasattr(purchase_data, 'items'):
            for key, value in purchase_data.items():
                payload[key] = value
        else:
            payload = dict(purchase_data)

        result = service.execute({
            "command": "UpdatePurchaseOrder",
            "tenant_id": tenant_id,
            "entity_id": purchase_id,
            **payload
        })

        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to update purchase"))

        return result["data"]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(204)
    def delete(self, purchase_id, tenant_id):
        """Delete a purchase order"""
        service = get_purchase_service()
        result = service.execute({
            "command": "DeletePurchaseOrder",
            "tenant_id": tenant_id,
            "entity_id": purchase_id
        })

        if not result.get("success"):
            abort(409, message=result.get("error", "Failed to delete purchase"))

        return '', 204

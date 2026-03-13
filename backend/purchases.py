from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from .extensions import db
from .decorators import tenant_required
from .schemas import PurchaseOrderSchema, BaseSchema
from backend.purchases_service import get_purchase_service

blp = Blueprint("purchases", __name__, description="Operations on purchase orders")


@blp.route("/purchase-orders")
class PurchaseOrderList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, PurchaseOrderSchema(many=True))
    def get(self, tenant_id):
        """List purchase orders"""
        service = get_purchase_service()
        result = service.execute({
            "command": "ListPurchaseOrders",
            "tenant_id": tenant_id
        })
        
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to list orders"))
        
        return result["data"]["items"]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.arguments(PurchaseOrderSchema)
    @blp.response(201, PurchaseOrderSchema)
    def post(self, order_data, tenant_id):
        """Create a new purchase order"""
        service = get_purchase_service()
        
        lines = []
        if hasattr(order_data, 'lines'):
            for line in order_data.lines:
                lines.append({
                    "product_id": line.product_id if hasattr(line, 'product_id') else line.get('product_id'),
                    "description": line.description if hasattr(line, 'description') else line.get('description', ''),
                    "quantity": line.quantity if hasattr(line, 'quantity') else line.get('quantity', 1),
                    "unit_price": line.unit_price if hasattr(line, 'unit_price') else line.get('unit_price', 0)
                })
        
        expected_date = ''
        if hasattr(order_data, 'expected_date') and order_data.expected_date:
            expected_date = order_data.expected_date.isoformat()
        
        result = service.execute({
            "command": "CreatePurchaseOrder",
            "tenant_id": tenant_id,
            "number": order_data.number if hasattr(order_data, 'number') else order_data.get('number'),
            "date": order_data.date.isoformat() if hasattr(order_data, 'date') else str(order_data.get('date', '')),
            "supplier_id": order_data.supplier_id if hasattr(order_data, 'supplier_id') else order_data.get('supplier_id'),
            "expected_date": expected_date,
            "notes": order_data.notes if hasattr(order_data, 'notes') else order_data.get('notes', ''),
            "lines": lines
        })
        
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to create order"))
        
        return result["data"], 201


@blp.route("/purchase-orders/<int:order_id>")
class PurchaseOrderResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, PurchaseOrderSchema)
    def get(self, order_id, tenant_id):
        """Get purchase order by ID"""
        service = get_purchase_service()
        result = service.execute({
            "command": "GetPurchaseOrder",
            "tenant_id": tenant_id,
            "entity_id": order_id
        })
        
        if not result.get("success"):
            abort(404, message=result.get("error", "Purchase order not found"))
        
        return result["data"]
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.arguments(BaseSchema)
    @blp.response(200, PurchaseOrderSchema)
    def put(self, order_data, order_id, tenant_id):
        """Update a purchase order"""
        service = get_purchase_service()
        
        payload = {}
        if hasattr(order_data, 'items'):
            for key, value in order_data.items():
                if key != 'lines':
                    payload[key] = value
        else:
            for key, value in order_data.items():
                if key != 'lines':
                    payload[key] = value
        
        result = service.execute({
            "command": "UpdatePurchaseOrder",
            "tenant_id": tenant_id,
            "entity_id": order_id,
            **payload
        })
        
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to update order"))
        
        return result["data"]
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(204)
    def delete(self, order_id, tenant_id):
        """Delete a purchase order"""
        service = get_purchase_service()
        result = service.execute({
            "command": "DeletePurchaseOrder",
            "tenant_id": tenant_id,
            "entity_id": order_id
        })
        
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to delete order"))
        
        return '', 204


@blp.route("/purchase-orders/<int:order_id>/confirm")
class PurchaseOrderConfirm(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, PurchaseOrderSchema)
    def post(self, order_id, tenant_id):
        """Confirm a purchase order"""
        service = get_purchase_service()
        result = service.execute({
            "command": "ConfirmPurchaseOrder",
            "tenant_id": tenant_id,
            "entity_id": order_id
        })
        
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to confirm order"))
        
        return result["data"]


@blp.route("/purchase-orders/<int:order_id>/receive")
class PurchaseOrderReceive(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, PurchaseOrderSchema)
    def post(self, order_id, tenant_id):
        """Mark purchase order as received"""
        service = get_purchase_service()
        result = service.execute({
            "command": "ReceivePurchaseOrder",
            "tenant_id": tenant_id,
            "entity_id": order_id
        })
        
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to receive order"))
        
        return result["data"]


@blp.route("/purchase-orders/<int:order_id>/cancel")
class PurchaseOrderCancel(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, PurchaseOrderSchema)
    def post(self, order_id, tenant_id):
        """Cancel a purchase order"""
        service = get_purchase_service()
        result = service.execute({
            "command": "CancelPurchaseOrder",
            "tenant_id": tenant_id,
            "entity_id": order_id
        })
        
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to cancel order"))
        
        return result["data"]

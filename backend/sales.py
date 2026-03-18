from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from .extensions import db
from .decorators import tenant_required
from .schemas import SalesOrderSchema, BaseSchema
from backend.sales_service import get_sales_service

blp = Blueprint("sales", __name__, description="Operations on sales orders")


@blp.route("/sales-orders")
class SalesOrderList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, SalesOrderSchema(many=True))
    def get(self, tenant_id):
        """List sales orders"""
        service = get_sales_service()
        result = service.execute({
            "command": "ListSalesOrders",
            "tenant_id": tenant_id
        })
        
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to list orders"))
        
        return result["data"]["items"]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.arguments(SalesOrderSchema)
    @blp.response(201, SalesOrderSchema)
    def post(self, order_data, tenant_id):
        """Create a new order"""
        service = get_sales_service()
        
        lines = []
        if hasattr(order_data, 'lines'):
            for line in order_data.lines:
                lines.append({
                    "product_id": line.product_id if hasattr(line, 'product_id') else line.get('product_id'),
                    "description": line.description if hasattr(line, 'description') else line.get('description', ''),
                    "quantity": line.quantity if hasattr(line, 'quantity') else line.get('quantity', 1),
                    "unit_price": line.unit_price if hasattr(line, 'unit_price') else line.get('unit_price', 0)
                })
        
        result = service.execute({
            "command": "CreateSalesOrder",
            "tenant_id": tenant_id,
            "number": order_data.number if hasattr(order_data, 'number') else order_data.get('number'),
            "date": order_data.date.isoformat() if hasattr(order_data, 'date') else str(order_data.get('date', '')),
            "customer_id": order_data.customer_id if hasattr(order_data, 'customer_id') else order_data.get('customer_id'),
            "notes": order_data.notes if hasattr(order_data, 'notes') else order_data.get('notes', ''),
            "lines": lines
        })
        
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to create order"))
        
        return result["data"], 201


@blp.route("/sales-orders/<int:order_id>")
class SalesOrderResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, SalesOrderSchema)
    def get(self, order_id, tenant_id):
        """Get sales order by ID"""
        service = get_sales_service()
        result = service.execute({
            "command": "GetSalesOrder",
            "tenant_id": tenant_id,
            "entity_id": order_id
        })
        
        if not result.get("success"):
            abort(404, message=result.get("error", "Sales order not found"))
        
        return result["data"]
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.arguments(BaseSchema)
    @blp.response(200, SalesOrderSchema)
    def put(self, order_data, order_id, tenant_id):
        """Update a sales order"""
        service = get_sales_service()
        
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
            "command": "UpdateSalesOrder",
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
        """Delete a sales order"""
        service = get_sales_service()
        result = service.execute({
            "command": "DeleteSalesOrder",
            "tenant_id": tenant_id,
            "entity_id": order_id
        })
        
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to delete order"))
        
        return '', 204


@blp.route("/sales-orders/<int:order_id>/confirm")
class SalesOrderConfirm(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, SalesOrderSchema)
    def post(self, order_id, tenant_id):
        """Confirm a sales order"""
        service = get_sales_service()
        result = service.execute({
            "command": "ConfirmSalesOrder",
            "tenant_id": tenant_id,
            "entity_id": order_id
        })
        
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to confirm order"))
        
        return result["data"]


@blp.route("/sales-orders/<int:order_id>/cancel")
class SalesOrderCancel(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, SalesOrderSchema)
    def post(self, order_id, tenant_id):
        """Cancel a sales order"""
        service = get_sales_service()
        result = service.execute({
            "command": "CancelSalesOrder",
            "tenant_id": tenant_id,
            "entity_id": order_id
        })
        
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to cancel order"))
        
        return result["data"]

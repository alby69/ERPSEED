from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from .models import SalesOrder, SalesOrderLine
from backend.entities.soggetto import Soggetto
from .extensions import db
from .schemas import SalesOrderSchema
from .utils import apply_filters, paginate, apply_sorting, apply_date_filters
from .core.services.tenant_context import TenantContext

blp = Blueprint("sales", __name__, description="Operations on sales orders")

def get_tenant_query(model):
    """Get query filtered by current tenant."""
    tenant_id = TenantContext.get_tenant_id()
    if tenant_id is None:
        abort(403, message="Tenant context not found")
    return model.query.filter_by(tenant_id=tenant_id)

@blp.route("/sales-orders")
class SalesOrderList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, SalesOrderSchema(many=True))
    def get(self):
        """List sales orders"""
        query = get_tenant_query(SalesOrder)
        query = apply_filters(query, SalesOrder, ['number'])
        query = apply_date_filters(query, SalesOrder, 'date')
        query = apply_sorting(query, SalesOrder)
        items, headers = paginate(query)
        return items, 200, headers

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(SalesOrderSchema)
    @blp.response(201, SalesOrderSchema)
    def post(self, order_data):
        """Create a new order"""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        
        order_data.tenant_id = tenant_id
        
        if not Soggetto.query.filter_by(id=order_data.customer_id, tenant_id=tenant_id).first():
            abort(404, message="Customer not found")

        for line in order_data.lines:
            line.tenant_id = tenant_id
            
        db.session.add(order_data)
        db.session.commit()
        return order_data

@blp.route("/sales-orders/<int:order_id>")
class SalesOrderResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, SalesOrderSchema)
    def get(self, order_id):
        """Get sales order by ID"""
        query = get_tenant_query(SalesOrder)
        order = query.get(order_id)
        if not order:
            abort(404, message="Sales order not found")
        return order
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(SalesOrderSchema)
    @blp.response(200, SalesOrderSchema)
    def put(self, order_data, order_id):
        """Update a sales order"""
        query = get_tenant_query(SalesOrder)
        order = query.get(order_id)
        if not order:
            abort(404, message="Sales order not found")
        
        for key, value in order_data.items():
            if key == 'lines':
                continue
            if hasattr(order, key):
                setattr(order, key, value)
        
        db.session.commit()
        return order
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, order_id):
        """Delete a sales order"""
        query = get_tenant_query(SalesOrder)
        order = query.get(order_id)
        if not order:
            abort(404, message="Sales order not found")
        
        db.session.delete(order)
        db.session.commit()
        return '', 204


@blp.route("/sales-orders/<int:order_id>/confirm")
class SalesOrderConfirm(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, SalesOrderSchema)
    def post(self, order_id):
        """Confirm a sales order"""
        query = get_tenant_query(SalesOrder)
        order = query.get(order_id)
        if not order:
            abort(404, message="Sales order not found")
        
        if order.status != 'draft':
            abort(400, message="Only draft orders can be confirmed")
        
        order.status = 'confirmed'
        db.session.commit()
        return order


@blp.route("/sales-orders/<int:order_id>/cancel")
class SalesOrderCancel(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, SalesOrderSchema)
    def post(self, order_id):
        """Cancel a sales order"""
        query = get_tenant_query(SalesOrder)
        order = query.get(order_id)
        if not order:
            abort(404, message="Sales order not found")
        
        if order.status in ['completed', 'cancelled']:
            abort(400, message="Order cannot be cancelled in current status")
        
        order.status = 'cancelled'
        db.session.commit()
        return order
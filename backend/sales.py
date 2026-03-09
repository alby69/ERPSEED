from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from .models import SalesOrder, SalesOrderLine
from backend.entities.soggetto import Soggetto
from .extensions import db, ma
from .decorators import tenant_required
from .schemas import SalesOrderSchema, BaseSchema
from .utils import apply_filters, paginate, apply_sorting, apply_date_filters
from .core.services.tenant_context import TenantContext
from .services.generic_service import generic_service

blp = Blueprint("sales", __name__, description="Operations on sales orders")

class SalesOrderUpdateSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = SalesOrder
        load_instance = False
        exclude = BaseSchema.Meta.exclude + ("date",)

@blp.route("/sales-orders")
class SalesOrderList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, SalesOrderSchema(many=True))
    def get(self, tenant_id):
        """List sales orders"""
        query = SalesOrder.query.filter_by(tenant_id=tenant_id)
        query = apply_filters(query, SalesOrder, ['number'])
        query = apply_date_filters(query, SalesOrder, 'date')
        query = apply_sorting(query, SalesOrder)
        items, headers = paginate(query)
        return items, 200, headers

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.arguments(SalesOrderSchema)
    @blp.response(201, SalesOrderSchema)
    def post(self, order_data, tenant_id):
        """Create a new order"""
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
    @tenant_required
    @blp.response(200, SalesOrderSchema)
    def get(self, order_id, tenant_id):
        """Get sales order by ID"""
        return generic_service.get_tenant_resource(
            SalesOrder, order_id, tenant_id, not_found_message="Sales order not found"
        )
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.arguments(SalesOrderUpdateSchema(partial=True))
    @blp.response(200, SalesOrderSchema)
    def put(self, order_data, order_id, tenant_id):
        """Update a sales order"""
        order = SalesOrder.query.filter_by(id=order_id, tenant_id=tenant_id).first()
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
    @tenant_required
    @blp.response(204)
    def delete(self, order_id, tenant_id):
        """Delete a sales order"""
        def check_status(order):
            if order.status not in ['draft', 'cancelled']:
                abort(400, message="Only draft or cancelled orders can be deleted.")

        generic_service.delete_tenant_resource(
            SalesOrder, order_id, tenant_id,
            pre_delete_check=check_status,
            not_found_message="Sales order not found"
        )
        return '', 204


@blp.route("/sales-orders/<int:order_id>/confirm")
class SalesOrderConfirm(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, SalesOrderSchema)
    def post(self, order_id, tenant_id):
        """Confirm a sales order"""
        order = SalesOrder.query.filter_by(id=order_id, tenant_id=tenant_id).first()
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
    @tenant_required
    @blp.response(200, SalesOrderSchema)
    def post(self, order_id, tenant_id):
        """Cancel a sales order"""
        order = SalesOrder.query.filter_by(id=order_id, tenant_id=tenant_id).first()
        if not order:
            abort(404, message="Sales order not found")
        
        if order.status in ['completed', 'cancelled']:
            abort(400, message="Order cannot be cancelled in current status")
        
        order.status = 'cancelled'
        db.session.commit()
        return order
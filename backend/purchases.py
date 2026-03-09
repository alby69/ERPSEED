from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from .models import PurchaseOrder, PurchaseOrderLine
from backend.entities.soggetto import Soggetto
from .extensions import db, ma
from .schemas import PurchaseOrderSchema, BaseSchema
from .utils import apply_filters, paginate, apply_sorting, apply_date_filters
from .decorators import tenant_required
from .services.generic_service import generic_service

blp = Blueprint("purchases", __name__, description="Operations on purchase orders")

class PurchaseOrderUpdateSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = PurchaseOrder
        load_instance = False
        exclude = BaseSchema.Meta.exclude + ("date",)


@blp.route("/purchase-orders")
class PurchaseOrderList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, PurchaseOrderSchema(many=True))
    def get(self, tenant_id):
        """List purchase orders"""
        query = PurchaseOrder.query.filter_by(tenant_id=tenant_id)
        query = apply_filters(query, PurchaseOrder, ['number'])
        query = apply_date_filters(query, PurchaseOrder, 'date')
        query = apply_sorting(query, PurchaseOrder)
        items, headers = paginate(query)
        return items, 200, headers

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.arguments(PurchaseOrderSchema)
    @blp.response(201, PurchaseOrderSchema)
    def post(self, order_data, tenant_id):
        """Create a new purchase order"""
        order_data.tenant_id = tenant_id
        
        if not Soggetto.query.filter_by(id=order_data.supplier_id, tenant_id=tenant_id).first():
            abort(404, message="Supplier not found")

        for line in order_data.lines:
            line.tenant_id = tenant_id
            
        db.session.add(order_data)
        db.session.commit()
        return order_data


@blp.route("/purchase-orders/<int:order_id>")
class PurchaseOrderResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, PurchaseOrderSchema)
    def get(self, order_id, tenant_id):
        """Get purchase order by ID"""
        return generic_service.get_tenant_resource(
            PurchaseOrder, order_id, tenant_id, not_found_message="Purchase order not found"
        )
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.arguments(PurchaseOrderUpdateSchema(partial=True))
    @blp.response(200, PurchaseOrderSchema)
    def put(self, order_data, order_id, tenant_id):
        """Update a purchase order"""
        order = PurchaseOrder.query.filter_by(id=order_id, tenant_id=tenant_id).first()
        if not order:
            abort(404, message="Purchase order not found")
        
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
        """Delete a purchase order"""
        generic_service.delete_tenant_resource(
            PurchaseOrder, order_id, tenant_id, not_found_message="Purchase order not found"
        )
        return '', 204


@blp.route("/purchase-orders/<int:order_id>/confirm")
class PurchaseOrderConfirm(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, PurchaseOrderSchema)
    def post(self, order_id, tenant_id):
        """Confirm a purchase order"""
        order = PurchaseOrder.query.filter_by(id=order_id, tenant_id=tenant_id).first()
        if not order:
            abort(404, message="Purchase order not found")
        
        if order.status != 'draft':
            abort(400, message="Only draft orders can be confirmed")
        
        order.status = 'confirmed'
        db.session.commit()
        return order


@blp.route("/purchase-orders/<int:order_id>/receive")
class PurchaseOrderReceive(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, PurchaseOrderSchema)
    def post(self, order_id, tenant_id):
        """Mark purchase order as received"""
        order = PurchaseOrder.query.filter_by(id=order_id, tenant_id=tenant_id).first()
        if not order:
            abort(404, message="Purchase order not found")
        
        if order.status not in ['confirmed', 'partial']:
            abort(400, message="Order must be confirmed to receive")
        
        order.status = 'received'
        db.session.commit()
        return order


@blp.route("/purchase-orders/<int:order_id>/cancel")
class PurchaseOrderCancel(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, PurchaseOrderSchema)
    def post(self, order_id, tenant_id):
        """Cancel a purchase order"""
        order = PurchaseOrder.query.filter_by(id=order_id, tenant_id=tenant_id).first()
        if not order:
            abort(404, message="Purchase order not found")
        
        if order.status in ['received', 'cancelled']:
            abort(400, message="Order cannot be cancelled in current status")
        
        order.status = 'cancelled'
        db.session.commit()
        return order

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from datetime import datetime, timedelta
from marshmallow import fields, Schema

from .extensions import db
from .core.services.tenant_context import TenantContext

blp = Blueprint("dashboard", __name__, description="Dashboard & KPI Operations")


def get_tenant_id():
    """Get current tenant ID."""
    tenant_id = TenantContext.get_tenant_id()
    if tenant_id is None:
        abort(403, message="Tenant context not found")
    return tenant_id


class KpiSchema(Schema):
    parties = fields.Dict(keys=fields.Str(), values=fields.Int())
    products = fields.Int()
    sales = fields.Dict(keys=fields.Str(), values=fields.Raw())
    purchases = fields.Dict(keys=fields.Str(), values=fields.Raw())

class SummarySchema(Schema):
    count = fields.Int()
    total = fields.Float()

class RecentOrderSchema(Schema):
    id = fields.Int()
    number = fields.Str()
    status = fields.Str()
    total_amount = fields.Float()
    date = fields.Date(allow_none=True)
    created_at = fields.DateTime(allow_none=True)
    customer_id = fields.Int(allow_none=True)
    supplier_id = fields.Int(allow_none=True)

@blp.route("/dashboard/kpi")
class DashboardKPI(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, KpiSchema)
    def get(self):
        """Get dashboard KPI summary"""
        tenant_id = get_tenant_id()
        
        from .models import Product, SalesOrder, PurchaseOrder
        from backend.entities.soggetto import Soggetto
        from backend.entities.ruolo import SoggettoRuolo, Ruolo
        
        # Count customers (soggetti with Cliente role)
        cliente_ruolo = Ruolo.query.filter_by(codice='Cliente', tenant_id=tenant_id).first()
        if cliente_ruolo:
            total_customers = SoggettoRuolo.query.filter_by(ruolo_id=cliente_ruolo.id).join(Soggetto).filter(Soggetto.tenant_id == tenant_id).count()
        else:
            total_customers = Soggetto.query.filter_by(tenant_id=tenant_id).count()
        
        # Count suppliers (soggetti with Fornitore role)
        fornitore_ruolo = Ruolo.query.filter_by(codice='Fornitore', tenant_id=tenant_id).first()
        if fornitore_ruolo:
            total_suppliers = SoggettoRuolo.query.filter_by(ruolo_id=fornitore_ruolo.id).join(Soggetto).filter(Soggetto.tenant_id == tenant_id).count()
        else:
            total_suppliers = 0
        
        total_products = Product.query.filter_by(tenant_id=tenant_id).count()
        
        total_sales = SalesOrder.query.filter_by(tenant_id=tenant_id).count()
        total_sales_amount = db.session.query(func.sum(SalesOrder.total_amount)).filter(
            SalesOrder.tenant_id == tenant_id
        ).scalar() or 0
        
        total_purchases = PurchaseOrder.query.filter_by(tenant_id=tenant_id).count()
        total_purchases_amount = db.session.query(func.sum(PurchaseOrder.total_amount)).filter(
            PurchaseOrder.tenant_id == tenant_id
        ).scalar() or 0
        
        return {
            'parties': {
                'customers': total_customers,
                'suppliers': total_suppliers,
            },
            'products': total_products,
            'sales': {
                'total_orders': total_sales,
                'total_amount': float(total_sales_amount),
            },
            'purchases': {
                'total_orders': total_purchases,
                'total_amount': float(total_purchases_amount),
            }
        }


@blp.route("/dashboard/sales-summary")
class SalesSummary(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, fields.Dict(keys=fields.Str(), values=fields.Nested(SummarySchema)))
    def get(self):
        """Get sales summary by status"""
        tenant_id = get_tenant_id()
        
        from .models import SalesOrder
        
        summary = db.session.query(
            SalesOrder.status,
            func.count(SalesOrder.id).label('count'),
            func.sum(SalesOrder.total_amount).label('total')
        ).filter(
            SalesOrder.tenant_id == tenant_id
        ).group_by(SalesOrder.status).all()
        
        result = {}
        for status, count, total in summary:
            result[status] = {
                'count': count,
                'total': float(total or 0)
            }
        
        return result


@blp.route("/dashboard/purchases-summary")
class PurchasesSummary(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, fields.Dict(keys=fields.Str(), values=fields.Nested(SummarySchema)))
    def get(self):
        """Get purchases summary by status"""
        tenant_id = get_tenant_id()
        
        from .models import PurchaseOrder
        
        summary = db.session.query(
            PurchaseOrder.status,
            func.count(PurchaseOrder.id).label('count'),
            func.sum(PurchaseOrder.total_amount).label('total')
        ).filter(
            PurchaseOrder.tenant_id == tenant_id
        ).group_by(PurchaseOrder.status).all()
        
        result = {}
        for status, count, total in summary:
            result[status] = {
                'count': count,
                'total': float(total or 0)
            }
        
        return result


@blp.route("/dashboard/recent-sales")
class RecentSales(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, RecentOrderSchema(many=True))
    def get(self):
        """Get recent sales orders"""
        tenant_id = get_tenant_id()
        
        from .models import SalesOrder
        
        recent = SalesOrder.query.filter_by(tenant_id=tenant_id).order_by(
            SalesOrder.created_at.desc()
        ).limit(10).all()
        
        return [{
            'id': order.id,
            'number': order.number,
            'customer_id': order.customer_id,
            'status': order.status,
            'total_amount': order.total_amount,
            'date': order.date.isoformat() if order.date else None,
            'created_at': order.created_at.isoformat() if order.created_at else None
        } for order in recent]


@blp.route("/dashboard/recent-purchases")
class RecentPurchases(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, RecentOrderSchema(many=True))
    def get(self):
        """Get recent purchase orders"""
        tenant_id = get_tenant_id()
        
        from .models import PurchaseOrder
        
        recent = PurchaseOrder.query.filter_by(tenant_id=tenant_id).order_by(
            PurchaseOrder.created_at.desc()
        ).limit(10).all()
        
        return [{
            'id': order.id,
            'number': order.number,
            'supplier_id': order.supplier_id,
            'status': order.status,
            'total_amount': order.total_amount,
            'date': order.date.isoformat() if order.date else None,
            'created_at': order.created_at.isoformat() if order.created_at else None
        } for order in recent]

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from .models import SalesOrder, SalesOrderLine, Party
from .extensions import db
from .schemas import SalesOrderSchema
from .utils import apply_filters, paginate, apply_sorting, apply_date_filters

blp = Blueprint("sales", __name__, description="Operations on sales orders")

@blp.route("/sales")
class SalesOrderList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, SalesOrderSchema(many=True))
    def get(self):
        """Lista ordini di vendita"""
        query = SalesOrder.query
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
        """Crea un nuovo ordine"""
        # Verifica esistenza cliente
        if not Party.query.get(order_data['customer_id']):
            abort(404, message="Customer not found")

        order = SalesOrder(
            number=order_data['number'],
            customer_id=order_data['customer_id']
        )
        db.session.add(order)
        db.session.commit()
        return order
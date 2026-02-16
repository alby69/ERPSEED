from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from .models import SalesOrder, SalesOrderLine, Party
from .extensions import db
from .schemas import SalesOrderSchema
from .utils import apply_filters, paginate, apply_sorting, apply_date_filters

blp = Blueprint("sales", __name__, description="Operations on sales orders")

@blp.route("/sales-orders")
class SalesOrderList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, SalesOrderSchema(many=True))
    def get(self):
        """List sales orders"""
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
        """Create a new order"""
        # order_data is a SalesOrder instance with nested SalesOrderLine instances
        # Marshmallow-SQLAlchemy with load_instance=True handles object creation.
        
        # The customer_id is already on the order_data object.
        # We just need to verify it exists.
        if not Party.query.get(order_data.customer_id):
            abort(404, message="Customer not found")

        # The order_data object is already a complete SalesOrder with lines.
        # We can just add it to the session.
        db.session.add(order_data)
        db.session.commit()
        return order_data
from flask import render_template, make_response
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required
from weasyprint import HTML
from backend.models import SalesOrder
from app.schemas import SalesOrderSchema
from backend.crud import register_crud_routes

blp = Blueprint("sales", __name__, description="Operations on sales orders")

register_crud_routes(
    blp,
    SalesOrder,
    SalesOrderSchema,
    url_prefix="/sales",
    # Semantic Search: Search in the order number OR in the related customer's name
    search_fields=["number", "customer.name"],
    # Semantic Load: Load customer and lines in a single query
    eager_load=["customer", "lines"]
)

@blp.route("/sales/<int:order_id>/pdf")
class SalesOrderPdf(MethodView):
    @jwt_required()
    def get(self, order_id):
        """Generate a PDF of the sales order"""
        order = SalesOrder.query.get_or_404(order_id)
        # Note: render_template will look in the root 'templates' folder if it exists,
        # or relative to the blueprint's folder. The file 'order_pdf.html' is in the root.
        html = render_template('order_pdf.html', order=order)
        pdf = HTML(string=html).write_pdf()
        
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=order_{order.number}.pdf'
        return response
from flask import render_template, make_response
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required
from weasyprint import HTML
from app.models.sales import SalesOrder
from app.schemas import SalesOrderSchema
from app.crud import register_crud_routes

blp = Blueprint("sales", __name__, description="Operations on sales orders")

register_crud_routes(
    blp,
    SalesOrder,
    SalesOrderSchema,
    url_prefix="/sales",
    # Semantic Search: Cerca nel numero ordine O nel nome del cliente correlato
    search_fields=["number", "customer.name"],
    # Semantic Load: Carica cliente e righe in un'unica query
    eager_load=["customer", "lines"]
)

@blp.route("/sales/<int:order_id>/pdf")
class SalesOrderPdf(MethodView):
    @jwt_required()
    def get(self, order_id):
        """Genera il PDF dell'ordine"""
        order = SalesOrder.query.get_or_404(order_id)
        html = render_template('order_pdf.html', order=order)
        pdf = HTML(string=html).write_pdf()
        
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=order_{order.number}.pdf'
        return response
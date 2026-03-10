"""
PDF Generation API per ERPSeed
Endpoint per generazione PDF di documenti
"""
from flask import request, send_file, abort
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from io import BytesIO
from backend.core.services.pdf_service import PDFService
from backend.core.services.tenant_context import TenantContext

pdf_bp = Blueprint('pdf', __name__, url_prefix='/api/v1/pdf', description='PDF Generation')


@pdf_bp.route('/sales-order/<int:order_id>')
class SalesOrderPDF(MethodView):
    @pdf_bp.response(200, content_type="application/pdf", schema={"type": "string", "format": "binary"})
    @jwt_required()
    def get(self, order_id):
        """
        Genera PDF per ordine di vendita.
        """
        user_id = get_jwt_identity()
        from backend.core.models.user import User
        user = User.query.get(user_id)
        
        if not user:
            abort(404, message="Utente non trovato")
        
        tenant_id = user.tenant_id
        
        try:
            pdf_content = PDFService.generate_sales_order(order_id, tenant_id)
            
            headers = {
                "Content-Disposition": f"attachment; filename=ordine_{order_id}.pdf"
            }
            return pdf_content, 200, headers
        except ValueError as e:
            abort(404, message=str(e))
        except Exception as e:
            abort(500, message=f"Errore generazione PDF: {str(e)}")


@pdf_bp.route('/invoice/<int:invoice_id>')
class InvoicePDF(MethodView):
    @pdf_bp.response(200, content_type="application/pdf", schema={"type": "string", "format": "binary"})
    @jwt_required()
    def get(self, invoice_id):
        """
        Genera PDF per fattura.
        """
        user_id = get_jwt_identity()
        from backend.core.models.user import User
        user = User.query.get(user_id)
        
        if not user:
            abort(404, message="Utente non trovato")
        
        tenant_id = user.tenant_id
        
        try:
            pdf_content = PDFService.generate_invoice(invoice_id, tenant_id)
            
            headers = {
                "Content-Disposition": f"attachment; filename=fattura_{invoice_id}.pdf"
            }
            return pdf_content, 200, headers
        except ValueError as e:
            abort(404, message=str(e))
        except Exception as e:
            abort(500, message=f"Errore generazione PDF: {str(e)}")


@pdf_bp.route('/quote/<int:quote_id>')
class QuotePDF(MethodView):
    @pdf_bp.response(200, content_type="application/pdf", schema={"type": "string", "format": "binary"})
    @jwt_required()
    def get(self, quote_id):
        """
        Genera PDF per preventivo.
        """
        user_id = get_jwt_identity()
        from backend.core.models.user import User
        user = User.query.get(user_id)
        
        if not user:
            abort(404, message="Utente non trovato")
        
        tenant_id = user.tenant_id
        
        try:
            pdf_content = PDFService.generate_quote(quote_id, tenant_id)
            
            headers = {
                "Content-Disposition": f"attachment; filename=preventivo_{quote_id}.pdf"
            }
            return pdf_content, 200, headers
        except ValueError as e:
            abort(404, message=str(e))
        except Exception as e:
            abort(500, message=f"Errore generazione PDF: {str(e)}")

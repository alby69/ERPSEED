from flask.views import MethodView
from flask import request, jsonify, Response
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required

from backend.extensions import db
from backend.plugins.accounting.models import Invoice, InvoiceLine
from backend.modules.entities.soggetto import Soggetto
from backend.core.models import Tenant
from .generator import generate_fattura_elettronica, xml_to_string

blp = Blueprint("fattura_elettronica", __name__, description="Fattura Elettronica XML API")


@blp.route("/api/v1/fattura-elettronica/generate/<int:invoice_id>")
class FatturaElettronicaGenerate(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, invoice_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        invoice = Invoice.query.filter_by(id=invoice_id, tenant_id=tenant_id).first()
        if not invoice:
            abort(404, message="Invoice not found")

        tenant = Tenant.query.get(tenant_id)
        if not tenant:
            abort(404, message="Tenant not found")

        cessionario = Soggetto.query.get(invoice.party_id)
        if not cessionario:
            abort(404, message="Invoice party not found")

        cedente_dict = {
            "partita_iva": tenant.vat_number if hasattr(tenant, "vat_number") else (tenant.fiscal_code or ""),
            "codice_fiscale": tenant.fiscal_code if hasattr(tenant, "fiscal_code") else "",
            "nome": tenant.name or "",
            "ragione_sociale": tenant.name or "",
            "nazione": tenant.country or "IT",
        }

        inv_lines = InvoiceLine.query.filter_by(invoice_id=invoice.id, tenant_id=tenant_id).all()
        lines_list = []
        for i, line in enumerate(inv_lines):
            lines_list.append({
                "_num": i + 1,
                "description": line.description,
                "quantity": line.quantity,
                "unit_price": line.unit_price,
                "tax_percent": line.tax_percent,
            })

        cessionario_dict = {
            "partita_iva": cessionario.partita_iva or "",
            "codice_fiscale": cessionario.codice_fiscale or "",
            "nome": cessionario.nome or "",
            "cognome": cessionario.cognome or "",
            "ragione_sociale": cessionario.ragione_sociale or (cessionario.nome or ""),
            "nazione": "IT",
            "indirizzo": "",
            "cap": "",
            "citta": "",
            "provincia": "",
        }

        xml_root = generate_fattura_elettronica(
            invoice, lines_list, cedente_dict, cessionario_dict, tenant
        )
        xml_str = xml_to_string(xml_root)
        filename = f"FE_{tenant_id:05d}_{invoice_id:05d}.xml"

        fmt = request.args.get("format", "xml")
        if fmt == "xml":
            return Response(xml_str, mimetype="application/xml",
                            headers={"Content-Disposition": f"attachment; filename={filename}"})
        return jsonify({"xml": xml_str, "filename": filename})


@blp.route("/api/v1/fattura-elettronica/validate/<int:invoice_id>")
class FatturaElettronicaValidate(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, invoice_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        invoice = Invoice.query.filter_by(id=invoice_id, tenant_id=tenant_id).first()
        if not invoice:
            abort(404, message="Invoice not found")
        if invoice.status != "sent":
            abort(400, message="Only sent invoices can be validated for XML export")
        return jsonify({"valid": True, "message": f"Invoice {invoice.invoice_number} is ready for XML export"})

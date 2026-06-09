from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

blp = Blueprint("invoicing", __name__, url_prefix="/api/v1/invoicing", description="Invoicing API")


def get_service():
    from ..service_api import get_invoicing_service
    return get_invoicing_service()


@blp.route("/invoices")
class InvoiceList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        result = get_service().execute({
            "command": "ListInvoices",
            "tenant_id": tenant_id,
            "status": request.args.get("status"),
            "party_id": request.args.get("party_id", type=int),
            "search": request.args.get("search"),
            "page": request.args.get("page", 1, type=int),
            "per_page": request.args.get("per_page", 20, type=int),
        })
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to list invoices"))
        return result.get("data", {})

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        result = get_service().execute({
            "command": "CreateInvoice",
            "tenant_id": tenant_id,
            "user_id": user_id,
            **data,
        })
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to create invoice"))
        return result.get("data", {}), 201


@blp.route("/invoices/<int:invoice_id>")
class InvoiceResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, invoice_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        result = get_service().execute({
            "command": "GetInvoice",
            "entity_id": invoice_id,
            "tenant_id": tenant_id,
        })
        if not result.get("success"):
            abort(404, message=result.get("error", "Invoice not found"))
        return result.get("data", {})

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, invoice_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        data = request.get_json() or {}
        result = get_service().execute({
            "command": "UpdateInvoice",
            "entity_id": invoice_id,
            "tenant_id": tenant_id,
            **data,
        })
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to update invoice"))
        return result.get("data", {})


@blp.route("/invoices/<int:invoice_id>/issue")
class InvoiceIssue(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, invoice_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        user_id = get_jwt_identity()
        result = get_service().execute({
            "command": "IssueInvoice",
            "entity_id": invoice_id,
            "tenant_id": tenant_id,
            "user_id": user_id,
        })
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to issue invoice"))
        return result.get("data", {})


@blp.route("/invoices/<int:invoice_id>/cancel")
class InvoiceCancel(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, invoice_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        data = request.get_json() or {}
        result = get_service().execute({
            "command": "CancelInvoice",
            "entity_id": invoice_id,
            "tenant_id": tenant_id,
            "reason": data.get("reason", ""),
        })
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to cancel invoice"))
        return result.get("data", {})


@blp.route("/invoices/<int:invoice_id>/pay")
class InvoicePay(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, invoice_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        data = request.get_json() or {}
        result = get_service().execute({
            "command": "PayInvoice",
            "entity_id": invoice_id,
            "tenant_id": tenant_id,
            "amount": data.get("amount", 0),
            "payment_date": data.get("payment_date"),
        })
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to pay invoice"))
        return result.get("data", {})


@blp.route("/from-sales-order/<int:sales_order_id>")
class InvoiceFromSalesOrder(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, sales_order_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        result = get_service().execute({
            "command": "CreateInvoiceFromSalesOrder",
            "tenant_id": tenant_id,
            "sales_order_id": sales_order_id,
            "user_id": user_id,
            "date": data.get("date"),
            "due_date": data.get("due_date"),
            "description": data.get("description", ""),
            "notes": data.get("notes", ""),
        })
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to create invoice from sales order"))
        return result.get("data", {}), 201

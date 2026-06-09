from datetime import date
from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required

from backend.extensions import db
from backend.models import (
    PurchaseRequest, PurchaseRequestLine,
    RFQ, RFQLine, SupplierQuotation, SupplierQuotationLine,
    Product,
)

blp = Blueprint("purchase_requests", __name__, description="Purchase Requests & RFQ API")


# ========== Helpers ==========

def pr_to_dict(pr):
    return {
        "id": pr.id, "number": pr.number, "request_date": pr.request_date.isoformat() if pr.request_date else None,
        "required_date": pr.required_date.isoformat() if pr.required_date else None,
        "requester_id": pr.requester_id, "department_id": pr.department_id,
        "status": pr.status, "notes": pr.notes,
        "lines": [{
            "id": l.id, "product_id": l.product_id,
            "product_name": l.product.name if l.product else None,
            "quantity": l.quantity, "notes": l.notes,
        } for l in (pr.lines or [])],
        "created_at": pr.created_at.isoformat() if pr.created_at else None,
    }

def rfq_to_dict(r):
    return {
        "id": r.id, "number": r.number, "rfq_date": r.rfq_date.isoformat() if r.rfq_date else None,
        "valid_until": r.valid_until.isoformat() if r.valid_until else None,
        "status": r.status, "purchase_request_id": r.purchase_request_id, "notes": r.notes,
        "lines": [{
            "id": l.id, "product_id": l.product_id,
            "product_name": l.product.name if l.product else None,
            "quantity": l.quantity,
        } for l in (r.lines or [])],
        "quotations": [q_to_dict(q) for q in (r.quotations or [])],
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }

def q_to_dict(q):
    return {
        "id": q.id, "rfq_id": q.rfq_id, "supplier_id": q.supplier_id,
        "quotation_date": q.quotation_date.isoformat() if q.quotation_date else None,
        "valid_until": q.valid_until.isoformat() if q.valid_until else None,
        "total_amount": q.total_amount, "status": q.status, "notes": q.notes,
        "lines": [{
            "id": l.id, "product_id": l.product_id,
            "product_name": l.product.name if l.product else None,
            "quantity": l.quantity, "unit_price": l.unit_price,
            "delivery_date": l.delivery_date.isoformat() if l.delivery_date else None,
        } for l in (q.lines or [])],
    }

def gen_number(tenant_id, prefix, model_cls):
    year = date.today().year
    p = f"{prefix}-{year}"
    last = model_cls.query.filter(
        model_cls.tenant_id == tenant_id,
        model_cls.number.like(f"{p}%")
    ).order_by(model_cls.number.desc()).first()
    last_num = int(last.number.split("-")[-1]) + 1 if last else 1
    return f"{p}-{last_num:05d}"


# ========== Purchase Requests ==========

@blp.route("/api/v1/purchase-requests")
class PurchaseRequestList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        status = request.args.get("status")
        q = PurchaseRequest.query.filter_by(tenant_id=tenant_id, deleted_at=None)
        if status: q = q.filter_by(status=status)
        return [pr_to_dict(p) for p in q.order_by(PurchaseRequest.request_date.desc()).all()]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        data = request.get_json() or {}
        if not data.get("request_date"):
            abort(400, message="request_date is required")
        lines_data = data.pop("lines", [])
        pr = PurchaseRequest(
            tenant_id=tenant_id, number=gen_number(tenant_id, "RQ", PurchaseRequest),
            **{k: v for k, v in data.items() if k in ("request_date", "required_date", "requester_id", "department_id", "status", "notes")})
        db.session.add(pr)
        db.session.flush()
        for ld in lines_data:
            line = PurchaseRequestLine(tenant_id=tenant_id, request_id=pr.id,
                                       product_id=ld["product_id"], quantity=ld["quantity"],
                                       notes=ld.get("notes"))
            db.session.add(line)
        db.session.commit()
        return pr_to_dict(PurchaseRequest.query.get(pr.id)), 201


@blp.route("/api/v1/purchase-requests/<int:pr_id>")
class PurchaseRequestDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, pr_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        pr = PurchaseRequest.query.filter_by(id=pr_id, tenant_id=tenant_id, deleted_at=None).first()
        if not pr: abort(404)
        return pr_to_dict(pr)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, pr_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        pr = PurchaseRequest.query.filter_by(id=pr_id, tenant_id=tenant_id, deleted_at=None).first()
        if not pr: abort(404)
        data = request.get_json() or {}
        for f in ("required_date", "status", "notes"):
            if f in data: setattr(pr, f, data[f])
        if "lines" in data:
            PurchaseRequestLine.query.filter_by(request_id=pr.id).delete()
            for ld in data["lines"]:
                line = PurchaseRequestLine(tenant_id=tenant_id, request_id=pr.id,
                                           product_id=ld["product_id"], quantity=ld["quantity"],
                                           notes=ld.get("notes"))
                db.session.add(line)
        db.session.commit()
        return pr_to_dict(PurchaseRequest.query.get(pr.id))

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, pr_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        pr = PurchaseRequest.query.filter_by(id=pr_id, tenant_id=tenant_id, deleted_at=None).first()
        if not pr: abort(404)
        db.session.delete(pr)
        db.session.commit()
        return {"message": "Deleted"}, 204


@blp.route("/api/v1/purchase-requests/<int:pr_id>/approve")
class PurchaseRequestApprove(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, pr_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        pr = PurchaseRequest.query.filter_by(id=pr_id, tenant_id=tenant_id, deleted_at=None).first()
        if not pr: abort(404)
        if pr.status != "pending": abort(400, message="Only pending requests can be approved")
        pr.status = "approved"
        db.session.commit()
        return pr_to_dict(pr)


# ========== RFQ ==========

@blp.route("/api/v1/rfqs")
class RFQList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        status = request.args.get("status")
        q = RFQ.query.filter_by(tenant_id=tenant_id, deleted_at=None)
        if status: q = q.filter_by(status=status)
        return [rfq_to_dict(r) for r in q.order_by(RFQ.rfq_date.desc()).all()]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        data = request.get_json() or {}
        if not data.get("rfq_date"):
            abort(400, message="rfq_date is required")
        lines_data = data.pop("lines", [])
        r = RFQ(
            tenant_id=tenant_id, number=gen_number(tenant_id, "RFQ", RFQ),
            **{k: v for k, v in data.items() if k in ("rfq_date", "valid_until", "status", "purchase_request_id", "notes")})
        db.session.add(r)
        db.session.flush()
        for ld in lines_data:
            line = RFQLine(tenant_id=tenant_id, rfq_id=r.id,
                           product_id=ld["product_id"], quantity=ld["quantity"])
            db.session.add(line)
        db.session.commit()
        return rfq_to_dict(RFQ.query.get(r.id)), 201


@blp.route("/api/v1/rfqs/<int:rfq_id>")
class RFQDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, rfq_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        r = RFQ.query.filter_by(id=rfq_id, tenant_id=tenant_id, deleted_at=None).first()
        if not r: abort(404)
        return rfq_to_dict(r)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, rfq_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        r = RFQ.query.filter_by(id=rfq_id, tenant_id=tenant_id, deleted_at=None).first()
        if not r: abort(404)
        data = request.get_json() or {}
        for f in ("valid_until", "status", "notes"):
            if f in data: setattr(r, f, data[f])
        if "lines" in data:
            RFQLine.query.filter_by(rfq_id=r.id).delete()
            for ld in data["lines"]:
                line = RFQLine(tenant_id=tenant_id, rfq_id=r.id,
                               product_id=ld["product_id"], quantity=ld["quantity"])
                db.session.add(line)
        db.session.commit()
        return rfq_to_dict(RFQ.query.get(r.id))

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, rfq_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        r = RFQ.query.filter_by(id=rfq_id, tenant_id=tenant_id, deleted_at=None).first()
        if not r: abort(404)
        db.session.delete(r)
        db.session.commit()
        return {"message": "Deleted"}, 204


# ========== Supplier Quotations ==========

@blp.route("/api/v1/rfqs/<int:rfq_id>/quotations")
class SupplierQuotationList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, rfq_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        r = RFQ.query.filter_by(id=rfq_id, tenant_id=tenant_id, deleted_at=None).first()
        if not r: abort(404)
        return [q_to_dict(q) for q in (r.quotations or [])]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, rfq_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        r = RFQ.query.filter_by(id=rfq_id, tenant_id=tenant_id, deleted_at=None).first()
        if not r: abort(404)
        data = request.get_json() or {}
        if not data.get("supplier_id"):
            abort(400, message="supplier_id is required")
        lines_data = data.pop("lines", [])
        total = sum(ld.get("quantity", 0) * ld.get("unit_price", 0) for ld in lines_data)
        q = SupplierQuotation(
            tenant_id=tenant_id, rfq_id=r.id,
            supplier_id=data["supplier_id"],
            quotation_date=data.get("quotation_date", date.today().isoformat()),
            valid_until=data.get("valid_until"),
            total_amount=total, notes=data.get("notes"),
        )
        db.session.add(q)
        db.session.flush()
        for ld in lines_data:
            line = SupplierQuotationLine(tenant_id=tenant_id, quotation_id=q.id,
                                         product_id=ld["product_id"],
                                         quantity=ld["quantity"],
                                         unit_price=ld["unit_price"],
                                         delivery_date=ld.get("delivery_date"))
            db.session.add(line)
        db.session.commit()
        return q_to_dict(SupplierQuotation.query.get(q.id)), 201


@blp.route("/api/v1/quotations/<int:q_id>/accept")
class SupplierQuotationAccept(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, q_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        q = SupplierQuotation.query.filter_by(id=q_id, tenant_id=tenant_id).first()
        if not q: abort(404)
        if q.status != "pending": abort(400, message="Only pending quotations can be accepted")
        q.status = "accepted"
        # Mark RFQ as ordered
        rfq = RFQ.query.get(q.rfq_id)
        if rfq: rfq.status = "ordered"
        db.session.commit()
        return q_to_dict(q)


@blp.route("/api/v1/quotations/<int:q_id>")
class SupplierQuotationDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, q_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        q = SupplierQuotation.query.filter_by(id=q_id, tenant_id=tenant_id).first()
        if not q: abort(404)
        return q_to_dict(q)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, q_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        q = SupplierQuotation.query.filter_by(id=q_id, tenant_id=tenant_id).first()
        if not q: abort(404)
        db.session.delete(q)
        db.session.commit()
        return {"message": "Deleted"}, 204

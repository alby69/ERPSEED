from datetime import date, timedelta
from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.extensions import db
from backend.models import Maturity

blp = Blueprint("maturities", __name__, description="Maturities / Scadenzario API")


def maturity_to_dict(m):
    return {
        "id": m.id,
        "tenant_id": m.tenant_id,
        "party_id": m.party_id,
        "due_date": m.due_date.isoformat() if m.due_date else None,
        "amount": m.amount,
        "paid_amount": m.paid_amount,
        "balance": m.balance,
        "reference_type": m.reference_type,
        "reference_id": m.reference_id,
        "reference_number": m.reference_number,
        "description": m.description,
        "status": m.status,
        "created_at": m.created_at.isoformat() if m.created_at else None,
        "updated_at": m.updated_at.isoformat() if m.updated_at else None,
    }


@blp.route("/api/v1/maturities")
class MaturityList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        status = request.args.get("status")
        party_id = request.args.get("party_id", type=int)
        overdue = request.args.get("overdue", type=bool)

        query = Maturity.query.filter_by(tenant_id=tenant_id, deleted_at=None)
        if status:
            query = query.filter_by(status=status)
        if party_id:
            query = query.filter_by(party_id=party_id)
        if overdue:
            query = query.filter(Maturity.due_date < date.today(), Maturity.status.in_(["open", "partial"]))
        query = query.order_by(Maturity.due_date.asc(), Maturity.id.desc())
        return [maturity_to_dict(m) for m in query.all()]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        data = request.get_json() or {}
        if not data.get("party_id") or not data.get("due_date") or data.get("amount") is None:
            abort(400, message="party_id, due_date, and amount are required")
        m = Maturity(
            tenant_id=tenant_id,
            party_id=data["party_id"],
            due_date=data["due_date"],
            amount=float(data["amount"]),
            balance=float(data["amount"]),
            reference_type=data.get("reference_type"),
            reference_id=data.get("reference_id"),
            reference_number=data.get("reference_number"),
            description=data.get("description", ""),
        )
        db.session.add(m)
        db.session.commit()
        return maturity_to_dict(m), 201


@blp.route("/api/v1/maturities/from-invoices")
class MaturityFromInvoices(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        return {"message": "0 maturities created from invoices (module not yet integrated)"}, 200


@blp.route("/api/v1/maturities/<int:maturity_id>")
class MaturityDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, maturity_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        m = Maturity.query.filter_by(id=maturity_id, tenant_id=tenant_id, deleted_at=None).first()
        if not m:
            abort(404, message="Maturity not found")
        return maturity_to_dict(m)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, maturity_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        m = Maturity.query.filter_by(id=maturity_id, tenant_id=tenant_id, deleted_at=None).first()
        if not m:
            abort(404, message="Maturity not found")
        data = request.get_json() or {}
        for field in ("due_date", "amount", "description", "status"):
            if field in data:
                setattr(m, field, data[field])
        if "paid_amount" in data:
            m.paid_amount = float(data["paid_amount"])
            m.balance = m.amount - m.paid_amount
            if m.balance <= 0.01:
                m.status = "paid"
                m.balance = 0
            elif m.paid_amount > 0:
                m.status = "partial"
        db.session.commit()
        return maturity_to_dict(m)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, maturity_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        m = Maturity.query.filter_by(id=maturity_id, tenant_id=tenant_id, deleted_at=None).first()
        if not m:
            abort(404, message="Maturity not found")
        db.session.delete(m)
        db.session.commit()
        return {"message": "Deleted"}, 204


@blp.route("/api/v1/maturities/summary")
class MaturitySummary(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        today = date.today()
        q = Maturity.query.filter_by(tenant_id=tenant_id, deleted_at=None)

        total_open = sum(m.balance for m in q.filter(Maturity.status.in_(["open", "partial"])).all())
        total_overdue = sum(m.balance for m in q.filter(
            Maturity.due_date < today, Maturity.status.in_(["open", "partial"])
        ).all())
        total_paid = sum(m.amount for m in q.filter_by(status="paid").all())
        due_30 = sum(m.balance for m in q.filter(
            Maturity.due_date.between(today, today + timedelta(days=30)),
            Maturity.status.in_(["open", "partial"]),
        ).all())

        return {
            "total_open": round(total_open, 2),
            "total_overdue": round(total_overdue, 2),
            "total_paid": round(total_paid, 2),
            "due_next_30_days": round(due_30, 2),
        }

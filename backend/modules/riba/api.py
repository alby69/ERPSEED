from datetime import date
from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required

from backend.extensions import db
from backend.models import RiBa, RiBaItem

blp = Blueprint("riba", __name__, description="Ri.Ba. API")


def riba_to_dict(r):
    return {
        "id": r.id, "number": r.number, "batch_date": r.batch_date.isoformat() if r.batch_date else None,
        "bank_name": r.bank_name, "bank_iban": r.bank_iban,
        "total_amount": r.total_amount, "collected_amount": r.collected_amount,
        "status": r.status, "notes": r.notes,
        "items": [{
            "id": i.id, "invoice_id": i.invoice_id, "maturity_id": i.maturity_id,
            "soggetto_id": i.soggetto_id, "soggetto_name": i.soggetto_name,
            "amount": i.amount, "due_date": i.due_date.isoformat() if i.due_date else None,
            "status": i.status,
        } for i in (r.items or [])],
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }


def generate_riba_number(tenant_id):
    year = date.today().year
    prefix = f"RIBA-{year}"
    last = RiBa.query.filter(
        RiBa.tenant_id == tenant_id,
        RiBa.number.like(f"{prefix}%")
    ).order_by(RiBa.number.desc()).first()
    last_num = int(last.number.split("-")[-1]) + 1 if last else 1
    return f"{prefix}-{last_num:05d}"


@blp.route("/api/v1/riba/batches")
class RiBaList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        status = request.args.get("status")
        q = RiBa.query.filter_by(tenant_id=tenant_id, deleted_at=None)
        if status: q = q.filter_by(status=status)
        return [riba_to_dict(r) for r in q.order_by(RiBa.batch_date.desc()).all()]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        data = request.get_json() or {}
        if not data.get("batch_date"):
            abort(400, message="batch_date is required")
        batch_date = data["batch_date"]
        if isinstance(batch_date, str): batch_date = date.fromisoformat(batch_date)

        items_data = data.pop("items", [])
        total = sum(it.get("amount", 0) for it in items_data)
        r = RiBa(
            tenant_id=tenant_id, number=generate_riba_number(tenant_id),
            batch_date=batch_date,
            bank_name=data.get("bank_name"), bank_iban=data.get("bank_iban"),
            total_amount=total, notes=data.get("notes"),
        )
        db.session.add(r)
        db.session.flush()
        for it in items_data:
            due = it.get("due_date")
            if isinstance(due, str): due = date.fromisoformat(due)
            item = RiBaItem(
                tenant_id=tenant_id, riba_id=r.id,
                invoice_id=it.get("invoice_id"), maturity_id=it.get("maturity_id"),
                soggetto_id=it["soggetto_id"], soggetto_name=it.get("soggetto_name"),
                amount=it["amount"], due_date=due,
            )
            db.session.add(item)
        db.session.commit()
        return riba_to_dict(RiBa.query.get(r.id)), 201


@blp.route("/api/v1/riba/batches/<int:batch_id>")
class RiBaDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, batch_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        r = RiBa.query.filter_by(id=batch_id, tenant_id=tenant_id, deleted_at=None).first()
        if not r: abort(404)
        return riba_to_dict(r)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, batch_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        r = RiBa.query.filter_by(id=batch_id, tenant_id=tenant_id, deleted_at=None).first()
        if not r: abort(404)
        data = request.get_json() or {}
        for f in ("bank_name", "bank_iban", "notes", "status", "collected_amount"):
            if f in data: setattr(r, f, data[f])
        if "items" in data:
            RiBaItem.query.filter_by(riba_id=r.id).delete()
            for it in data["items"]:
                due = it.get("due_date")
                if isinstance(due, str): due = date.fromisoformat(due)
                item = RiBaItem(
                    tenant_id=tenant_id, riba_id=r.id,
                    invoice_id=it.get("invoice_id"), maturity_id=it.get("maturity_id"),
                    soggetto_id=it["soggetto_id"], soggetto_name=it.get("soggetto_name"),
                    amount=it["amount"], due_date=due,
                )
                db.session.add(item)
            r.total_amount = sum(it.get("amount", 0) for it in data["items"])
        db.session.commit()
        return riba_to_dict(RiBa.query.get(r.id))

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, batch_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        r = RiBa.query.filter_by(id=batch_id, tenant_id=tenant_id, deleted_at=None).first()
        if not r: abort(404)
        db.session.delete(r)
        db.session.commit()
        return {"message": "Deleted"}, 204


@blp.route("/api/v1/riba/batches/<int:batch_id>/send")
class RiBaSend(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, batch_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        r = RiBa.query.filter_by(id=batch_id, tenant_id=tenant_id, deleted_at=None).first()
        if not r: abort(404)
        if r.status != "draft": abort(400, message="Only draft batches can be sent")
        r.status = "sent"
        db.session.commit()
        return riba_to_dict(r)


@blp.route("/api/v1/riba/items/<int:item_id>/collect")
class RiBaItemCollect(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, item_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        item = RiBaItem.query.filter_by(id=item_id, tenant_id=tenant_id).first()
        if not item: abort(404)
        item.status = "collected"
        # Update parent batch collected amount
        batch = RiBa.query.get(item.riba_id)
        if batch:
            collected = db.session.query(db.func.coalesce(db.func.sum(RiBaItem.amount), 0))\
                .filter(RiBaItem.riba_id == batch.id, RiBaItem.status == "collected").scalar()
            batch.collected_amount = float(collected)
            if batch.collected_amount >= batch.total_amount:
                batch.status = "collected"
            else:
                batch.status = "partially_collected"
        db.session.commit()
        return {"message": "Collected", "item_id": item_id}


@blp.route("/api/v1/riba/items/<int:item_id>/reject")
class RiBaItemReject(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, item_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        item = RiBaItem.query.filter_by(id=item_id, tenant_id=tenant_id).first()
        if not item: abort(404)
        item.status = "rejected"
        db.session.commit()
        return {"message": "Rejected", "item_id": item_id}

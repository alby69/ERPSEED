from datetime import date
from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required

from backend.extensions import db
from backend.models import Contract

blp = Blueprint("contracts", __name__, description="Contracts API")


def contract_to_dict(c):
    return {
        "id": c.id, "tenant_id": c.tenant_id, "number": c.number, "name": c.name,
        "party_id": c.party_id,
        "start_date": c.start_date.isoformat() if c.start_date else None,
        "end_date": c.end_date.isoformat() if c.end_date else None,
        "value": c.value, "status": c.status, "notes": c.notes,
        "auto_renew": c.auto_renew, "renewal_notice_days": c.renewal_notice_days,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


@blp.route("/api/v1/contracts")
class ContractList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        status = request.args.get("status")
        query = Contract.query.filter_by(tenant_id=tenant_id, deleted_at=None)
        if status:
            query = query.filter_by(status=status)
        query = query.order_by(Contract.start_date.desc())
        return [contract_to_dict(c) for c in query.all()]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        data = request.get_json() or {}
        if not data.get("name") or not data.get("party_id") or not data.get("start_date"):
            abort(400, message="name, party_id, and start_date are required")
        c = Contract(
            tenant_id=tenant_id,
            number=data.get("number", generate_number(tenant_id)),
            name=data["name"], party_id=data["party_id"],
            start_date=data["start_date"], end_date=data.get("end_date"),
            value=float(data.get("value", 0)),
            notes=data.get("notes"), auto_renew=data.get("auto_renew", False),
            renewal_notice_days=int(data.get("renewal_notice_days", 30)),
        )
        db.session.add(c)
        db.session.commit()
        return contract_to_dict(c), 201


@blp.route("/api/v1/contracts/<int:contract_id>")
class ContractDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, contract_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        c = Contract.query.filter_by(id=contract_id, tenant_id=tenant_id, deleted_at=None).first()
        if not c: abort(404, message="Contract not found")
        return contract_to_dict(c)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, contract_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        c = Contract.query.filter_by(id=contract_id, tenant_id=tenant_id, deleted_at=None).first()
        if not c: abort(404, message="Contract not found")
        for f in ("name", "party_id", "start_date", "end_date", "value", "status", "notes", "auto_renew", "renewal_notice_days"):
            if f in request.get_json():
                setattr(c, f, request.get_json()[f])
        db.session.commit()
        return contract_to_dict(c)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, contract_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        c = Contract.query.filter_by(id=contract_id, tenant_id=tenant_id, deleted_at=None).first()
        if not c: abort(404, message="Contract not found")
        db.session.delete(c)
        db.session.commit()
        return {"message": "Deleted"}, 204


def generate_number(tenant_id):
    year = date.today().year
    prefix = f"CONT-{year}"
    last = Contract.query.filter(
        Contract.tenant_id == tenant_id,
        Contract.number.like(f"{prefix}%")
    ).order_by(Contract.number.desc()).first()
    if last:
        last_num = int(last.number.split("-")[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    return f"{prefix}-{new_num:05d}"

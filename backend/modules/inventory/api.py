from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from marshmallow import Schema, fields

from backend.extensions import db, cache
from backend.models import MovementReason, ProductStock

blp = Blueprint("inventory_management", __name__, description="Inventory Management API")


def movement_reason_to_dict(r):
    return {
        "id": r.id,
        "tenant_id": r.tenant_id,
        "code": r.code,
        "name": r.name,
        "movement_type": r.movement_type,
        "is_active": r.is_active,
    }


# ========== Movement Reasons ==========

@blp.route("/api/v1/movement-reasons")
class MovementReasonList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        cache_key = f"movement_reasons:{tenant_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        reasons = MovementReason.query.filter_by(tenant_id=tenant_id, deleted_at=None).order_by(MovementReason.code).all()
        result = [movement_reason_to_dict(r) for r in reasons]
        cache.set(cache_key, result, timeout=300)
        return result

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        data = request.get_json() or {}
        if not data.get("code") or not data.get("name") or not data.get("movement_type"):
            abort(400, message="code, name, and movement_type are required")
        if data["movement_type"] not in ("in", "out", "transfer", "adjustment"):
            abort(400, message="movement_type must be one of: in, out, transfer, adjustment")
        existing = MovementReason.query.filter_by(tenant_id=tenant_id, code=data["code"]).first()
        if existing:
            abort(400, message=f"Movement reason '{data['code']}' already exists")
        r = MovementReason(tenant_id=tenant_id, code=data["code"], name=data["name"],
                           movement_type=data["movement_type"], is_active=data.get("is_active", True))
        db.session.add(r)
        db.session.commit()
        return movement_reason_to_dict(r), 201


@blp.route("/api/v1/movement-reasons/<int:reason_id>")
class MovementReasonDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, reason_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        r = MovementReason.query.filter_by(id=reason_id, tenant_id=tenant_id, deleted_at=None).first()
        if not r:
            abort(404, message="Movement reason not found")
        return movement_reason_to_dict(r)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, reason_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        r = MovementReason.query.filter_by(id=reason_id, tenant_id=tenant_id, deleted_at=None).first()
        if not r:
            abort(404, message="Movement reason not found")
        data = request.get_json() or {}
        for field in ("code", "name", "movement_type", "is_active"):
            if field in data:
                setattr(r, field, data[field])
        db.session.commit()
        return movement_reason_to_dict(r)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, reason_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        r = MovementReason.query.filter_by(id=reason_id, tenant_id=tenant_id, deleted_at=None).first()
        if not r:
            abort(404, message="Movement reason not found")
        db.session.delete(r)
        db.session.commit()
        return {"message": "Deleted"}, 204

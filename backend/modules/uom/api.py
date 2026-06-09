from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from backend.extensions import db
from backend.models import UnitOfMeasure

blp = Blueprint("uom", __name__, description="Units of Measure API")


def to_dict(uom):
    return {
        "id": uom.id,
        "tenant_id": uom.tenant_id,
        "code": uom.code,
        "name": uom.name,
        "symbol": uom.symbol,
        "description": uom.description,
        "is_active": uom.is_active,
        "created_at": uom.created_at.isoformat() if uom.created_at else None,
        "updated_at": uom.updated_at.isoformat() if uom.updated_at else None,
    }


@blp.route("/api/v1/units-of-measure")
class UomList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        items = UnitOfMeasure.query.filter_by(tenant_id=tenant_id, deleted_at=None).order_by(UnitOfMeasure.code).all()
        return [to_dict(i) for i in items]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        data = request.get_json() or {}
        if not data.get("code") or not data.get("name"):
            abort(400, message="code and name are required")
        existing = UnitOfMeasure.query.filter_by(tenant_id=tenant_id, code=data["code"]).first()
        if existing:
            abort(400, message=f"UoM with code '{data['code']}' already exists")
        item = UnitOfMeasure(tenant_id=tenant_id, code=data["code"], name=data["name"],
                             symbol=data.get("symbol"), description=data.get("description"),
                             is_active=data.get("is_active", True))
        db.session.add(item)
        db.session.commit()
        return to_dict(item), 201


@blp.route("/api/v1/units-of-measure/<int:item_id>")
class UomDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, item_id):
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        item = UnitOfMeasure.query.filter_by(id=item_id, tenant_id=tenant_id, deleted_at=None).first()
        if not item:
            abort(404, message="Unit of measure not found")
        return to_dict(item)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, item_id):
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        item = UnitOfMeasure.query.filter_by(id=item_id, tenant_id=tenant_id, deleted_at=None).first()
        if not item:
            abort(404, message="Unit of measure not found")
        data = request.get_json() or {}
        for field in ("code", "name", "symbol", "description", "is_active"):
            if field in data:
                setattr(item, field, data[field])
        db.session.commit()
        return to_dict(item)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, item_id):
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        item = UnitOfMeasure.query.filter_by(id=item_id, tenant_id=tenant_id, deleted_at=None).first()
        if not item:
            abort(404, message="Unit of measure not found")
        db.session.delete(item)
        db.session.commit()
        return {"message": "Deleted"}, 204

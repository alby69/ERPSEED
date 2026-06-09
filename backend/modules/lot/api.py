from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required

from backend.extensions import db
from backend.models import Lot, SerialNumber, Product

blp = Blueprint("lot", __name__, description="Lot & Serial Number API")


def lot_to_dict(l):
    return {
        "id": l.id, "tenant_id": l.tenant_id, "code": l.code,
        "product_id": l.product_id, "product_name": l.product.name if l.product else None,
        "supplier_id": l.supplier_id,
        "quantity": l.quantity, "initial_quantity": l.initial_quantity,
        "manufacturing_date": l.manufacturing_date.isoformat() if l.manufacturing_date else None,
        "expiry_date": l.expiry_date.isoformat() if l.expiry_date else None,
        "notes": l.notes,
        "created_at": l.created_at.isoformat() if l.created_at else None,
    }


def serial_to_dict(s):
    return {
        "id": s.id, "tenant_id": s.tenant_id, "code": s.code,
        "product_id": s.product_id, "product_name": s.product.name if s.product else None,
        "lot_id": s.lot_id,
        "status": s.status,
        "order_id": s.order_id, "order_type": s.order_type,
        "sold_date": s.sold_date.isoformat() if s.sold_date else None,
        "notes": s.notes,
        "created_at": s.created_at.isoformat() if s.created_at else None,
    }


# ========== Lots ==========

@blp.route("/api/v1/lots")
class LotList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        product_id = request.args.get("product_id", type=int)
        q = Lot.query.filter_by(tenant_id=tenant_id, deleted_at=None)
        if product_id: q = q.filter_by(product_id=product_id)
        return [lot_to_dict(l) for l in q.order_by(Lot.created_at.desc()).all()]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        data = request.get_json() or {}
        if not data.get("code") or not data.get("product_id"):
            abort(400, message="code and product_id are required")
        if not data.get("quantity"):
            abort(400, message="quantity is required")
        l = Lot(
            tenant_id=tenant_id,
            code=data["code"], product_id=data["product_id"],
            supplier_id=data.get("supplier_id"),
            quantity=data["quantity"], initial_quantity=data["quantity"],
            manufacturing_date=data.get("manufacturing_date"),
            expiry_date=data.get("expiry_date"),
            notes=data.get("notes"),
        )
        db.session.add(l)
        db.session.commit()
        return lot_to_dict(l), 201


@blp.route("/api/v1/lots/<int:lot_id>")
class LotDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, lot_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        l = Lot.query.filter_by(id=lot_id, tenant_id=tenant_id, deleted_at=None).first()
        if not l: abort(404)
        return lot_to_dict(l)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, lot_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        l = Lot.query.filter_by(id=lot_id, tenant_id=tenant_id, deleted_at=None).first()
        if not l: abort(404)
        for f in ("quantity", "manufacturing_date", "expiry_date", "notes"):
            if f in request.get_json(): setattr(l, f, request.get_json()[f])
        db.session.commit()
        return lot_to_dict(l)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, lot_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        l = Lot.query.filter_by(id=lot_id, tenant_id=tenant_id, deleted_at=None).first()
        if not l: abort(404)
        db.session.delete(l)
        db.session.commit()
        return {"message": "Deleted"}, 204


# ========== Serial Numbers ==========

@blp.route("/api/v1/serial-numbers")
class SerialNumberList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        product_id = request.args.get("product_id", type=int)
        status = request.args.get("status")
        q = SerialNumber.query.filter_by(tenant_id=tenant_id, deleted_at=None)
        if product_id: q = q.filter_by(product_id=product_id)
        if status: q = q.filter_by(status=status)
        return [serial_to_dict(s) for s in q.order_by(SerialNumber.created_at.desc()).all()]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        data = request.get_json() or {}
        if not data.get("code") or not data.get("product_id"):
            abort(400, message="code and product_id are required")
        # Batch create
        if data.get("count", 1) > 1:
            created = []
            count = int(data["count"])
            base_code = data["code"]
            for i in range(count):
                code = f"{base_code}-{i+1:04d}" if count > 1 else base_code
                existing = SerialNumber.query.filter_by(tenant_id=tenant_id, code=code, deleted_at=None).first()
                if existing: continue
                s = SerialNumber(tenant_id=tenant_id, code=code, product_id=data["product_id"],
                                 lot_id=data.get("lot_id"))
                db.session.add(s)
                created.append(s)
            db.session.commit()
            return [serial_to_dict(s) for s in created], 201
        else:
            s = SerialNumber(tenant_id=tenant_id, code=data["code"], product_id=data["product_id"],
                             lot_id=data.get("lot_id"), notes=data.get("notes"))
            db.session.add(s)
            db.session.commit()
            return serial_to_dict(s), 201


@blp.route("/api/v1/serial-numbers/<int:serial_id>")
class SerialNumberDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, serial_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        s = SerialNumber.query.filter_by(id=serial_id, tenant_id=tenant_id, deleted_at=None).first()
        if not s: abort(404)
        return serial_to_dict(s)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, serial_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        s = SerialNumber.query.filter_by(id=serial_id, tenant_id=tenant_id, deleted_at=None).first()
        if not s: abort(404)
        for f in ("status", "order_id", "order_type", "sold_date", "notes", "lot_id"):
            if f in request.get_json(): setattr(s, f, request.get_json()[f])
        db.session.commit()
        return serial_to_dict(s)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, serial_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        s = SerialNumber.query.filter_by(id=serial_id, tenant_id=tenant_id, deleted_at=None).first()
        if not s: abort(404)
        db.session.delete(s)
        db.session.commit()
        return {"message": "Deleted"}, 204

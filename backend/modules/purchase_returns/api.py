from datetime import date
from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.extensions import db
from backend.models import PurchaseReturn, PurchaseReturnLine

blp = Blueprint("purchase_returns", __name__, description="Purchase Returns API")


def pr_to_dict(pr):
    return {
        "id": pr.id,
        "tenant_id": pr.tenant_id,
        "number": pr.number,
        "date": pr.date.isoformat() if pr.date else None,
        "supplier_id": pr.supplier_id,
        "purchase_order_id": pr.purchase_order_id,
        "goods_receipt_id": pr.goods_receipt_id,
        "notes": pr.notes,
        "status": pr.status,
        "reason": pr.reason,
        "created_by": pr.created_by,
        "created_at": pr.created_at.isoformat() if pr.created_at else None,
        "updated_at": pr.updated_at.isoformat() if pr.updated_at else None,
        "lines": [
            {
                "id": l.id,
                "product_id": l.product_id,
                "description": l.description,
                "quantity": l.quantity,
                "unit_price": l.unit_price,
                "location_id": l.location_id,
            }
            for l in pr.lines
        ],
    }


@blp.route("/api/v1/purchase-returns")
class PurchaseReturnList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        status = request.args.get("status")
        query = PurchaseReturn.query.filter_by(tenant_id=tenant_id, deleted_at=None)
        if status:
            query = query.filter_by(status=status)
        query = query.order_by(PurchaseReturn.date.desc(), PurchaseReturn.id.desc())
        return [pr_to_dict(pr) for pr in query.all()]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        if not data.get("supplier_id"):
            abort(400, message="supplier_id is required")
        pr = PurchaseReturn(
            tenant_id=tenant_id,
            number=_generate_number(tenant_id),
            date=date.fromisoformat(data["date"]) if data.get("date") else date.today(),
            supplier_id=data["supplier_id"],
            purchase_order_id=data.get("purchase_order_id"),
            goods_receipt_id=data.get("goods_receipt_id"),
            notes=data.get("notes", ""),
            status="draft",
            reason=data.get("reason", ""),
            created_by=user_id,
        )
        db.session.add(pr)
        db.session.flush()
        for line_data in data.get("lines", []):
            line = PurchaseReturnLine(
                tenant_id=tenant_id,
                purchase_return_id=pr.id,
                product_id=line_data["product_id"],
                description=line_data.get("description", ""),
                quantity=float(line_data.get("quantity", 1)),
                unit_price=float(line_data.get("unit_price", 0)),
                location_id=line_data.get("location_id"),
            )
            db.session.add(line)
        db.session.commit()
        return pr_to_dict(pr), 201


@blp.route("/api/v1/purchase-returns/<int:return_id>")
class PurchaseReturnDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, return_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        pr = PurchaseReturn.query.filter_by(id=return_id, tenant_id=tenant_id, deleted_at=None).first()
        if not pr:
            abort(404, message="Purchase return not found")
        return pr_to_dict(pr)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, return_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        pr = PurchaseReturn.query.filter_by(id=return_id, tenant_id=tenant_id, deleted_at=None).first()
        if not pr:
            abort(404, message="Purchase return not found")
        if pr.status == "completed":
            abort(400, message="Cannot modify a completed purchase return")
        data = request.get_json() or {}
        for field in ("supplier_id", "purchase_order_id", "goods_receipt_id", "notes", "reason"):
            if field in data:
                setattr(pr, field, data[field])
        if "date" in data:
            pr.date = date.fromisoformat(data["date"])
        if "lines" in data:
            PurchaseReturnLine.query.filter_by(purchase_return_id=pr.id).delete()
            for line_data in data["lines"]:
                line = PurchaseReturnLine(
                    tenant_id=tenant_id, purchase_return_id=pr.id,
                    product_id=line_data["product_id"],
                    description=line_data.get("description", ""),
                    quantity=float(line_data.get("quantity", 1)),
                    unit_price=float(line_data.get("unit_price", 0)),
                    location_id=line_data.get("location_id"),
                )
                db.session.add(line)
        db.session.commit()
        return pr_to_dict(pr)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, return_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        pr = PurchaseReturn.query.filter_by(id=return_id, tenant_id=tenant_id, deleted_at=None).first()
        if not pr:
            abort(404, message="Purchase return not found")
        if pr.status == "completed":
            abort(400, message="Cannot delete a completed purchase return")
        db.session.delete(pr)
        db.session.commit()
        return {"message": "Deleted"}, 204


@blp.route("/api/v1/purchase-returns/<int:return_id>/complete")
class PurchaseReturnComplete(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, return_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        pr = PurchaseReturn.query.filter_by(id=return_id, tenant_id=tenant_id, deleted_at=None).first()
        if not pr:
            abort(404, message="Purchase return not found")
        if pr.status != "draft":
            abort(400, message=f"Cannot complete in status '{pr.status}'")
        for line in pr.lines:
            try:
                from datetime import datetime
                from backend.plugins.inventory.models import StockMovement, ProductStock
                stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
                sm = StockMovement(
                    tenant_id=tenant_id,
                    movement_number=f"PR-{pr.id}-{stamp}",
                    movement_type="out",
                    product_id=line.product_id,
                    location_id=line.location_id or 1,
                    quantity=line.quantity,
                    reference_type="purchase_return",
                    reference_id=pr.id,
                )
                db.session.add(sm)
                stock = ProductStock.query.filter_by(
                    tenant_id=tenant_id, product_id=line.product_id,
                    location_id=line.location_id or 1
                ).first()
                if stock:
                    stock.quantity -= line.quantity
                else:
                    stock = ProductStock(
                        tenant_id=tenant_id, product_id=line.product_id,
                        location_id=line.location_id or 1,
                        quantity=0,
                    )
                    db.session.add(stock)
            except ImportError:
                pass
        pr.status = "completed"
        db.session.commit()
        return pr_to_dict(pr)


def _generate_number(tenant_id):
    year = date.today().year
    prefix = f"R-{year}"
    last = PurchaseReturn.query.filter(
        PurchaseReturn.tenant_id == tenant_id,
        PurchaseReturn.number.like(f"{prefix}%")
    ).order_by(PurchaseReturn.number.desc()).first()
    if last:
        last_num = int(last.number.split("-")[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    return f"{prefix}-{new_num:05d}"

from datetime import date
from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.extensions import db
from backend.models import GoodsReceipt, GoodsReceiptLine

blp = Blueprint("goods_receipt", __name__, description="Goods Receipt API")


def gr_to_dict(gr):
    return {
        "id": gr.id,
        "tenant_id": gr.tenant_id,
        "number": gr.number,
        "date": gr.date.isoformat() if gr.date else None,
        "supplier_id": gr.supplier_id,
        "purchase_order_id": gr.purchase_order_id,
        "notes": gr.notes,
        "status": gr.status,
        "created_by": gr.created_by,
        "created_at": gr.created_at.isoformat() if gr.created_at else None,
        "updated_at": gr.updated_at.isoformat() if gr.updated_at else None,
        "lines": [
            {
                "id": l.id,
                "product_id": l.product_id,
                "purchase_order_line_id": l.purchase_order_line_id,
                "description": l.description,
                "quantity": l.quantity,
                "location_id": l.location_id,
            }
            for l in gr.lines
        ],
    }


@blp.route("/api/v1/goods-receipts")
class GoodsReceiptList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        status = request.args.get("status")
        query = GoodsReceipt.query.filter_by(tenant_id=tenant_id, deleted_at=None)
        if status:
            query = query.filter_by(status=status)
        query = query.order_by(GoodsReceipt.date.desc(), GoodsReceipt.id.desc())
        receipts = query.all()
        return [gr_to_dict(gr) for gr in receipts]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        if not data.get("supplier_id"):
            abort(400, message="supplier_id is required")
        gr = GoodsReceipt(
            tenant_id=tenant_id,
            number=generate_number(tenant_id),
            date=data.get("date", date.today().isoformat()),
            supplier_id=data["supplier_id"],
            purchase_order_id=data.get("purchase_order_id"),
            notes=data.get("notes", ""),
            status="draft",
            created_by=user_id,
        )
        db.session.add(gr)
        db.session.flush()
        for line_data in data.get("lines", []):
            line = GoodsReceiptLine(
                tenant_id=tenant_id,
                goods_receipt_id=gr.id,
                product_id=line_data["product_id"],
                purchase_order_line_id=line_data.get("purchase_order_line_id"),
                description=line_data.get("description", ""),
                quantity=float(line_data.get("quantity", 1)),
                location_id=line_data.get("location_id"),
            )
            db.session.add(line)
        db.session.commit()
        return gr_to_dict(gr), 201


@blp.route("/api/v1/goods-receipts/<int:receipt_id>")
class GoodsReceiptDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, receipt_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        gr = GoodsReceipt.query.filter_by(id=receipt_id, tenant_id=tenant_id, deleted_at=None).first()
        if not gr:
            abort(404, message="Goods receipt not found")
        return gr_to_dict(gr)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, receipt_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        gr = GoodsReceipt.query.filter_by(id=receipt_id, tenant_id=tenant_id, deleted_at=None).first()
        if not gr:
            abort(404, message="Goods receipt not found")
        if gr.status == "completed":
            abort(400, message="Cannot modify a completed goods receipt")
        data = request.get_json() or {}
        for field in ("supplier_id", "purchase_order_id", "notes", "date"):
            if field in data:
                setattr(gr, field, data[field])
        if "lines" in data:
            GoodsReceiptLine.query.filter_by(goods_receipt_id=gr.id).delete()
            for line_data in data["lines"]:
                line = GoodsReceiptLine(
                    tenant_id=tenant_id, goods_receipt_id=gr.id,
                    product_id=line_data["product_id"],
                    purchase_order_line_id=line_data.get("purchase_order_line_id"),
                    description=line_data.get("description", ""),
                    quantity=float(line_data.get("quantity", 1)),
                    location_id=line_data.get("location_id"),
                )
                db.session.add(line)
        db.session.commit()
        return gr_to_dict(gr)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, receipt_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        gr = GoodsReceipt.query.filter_by(id=receipt_id, tenant_id=tenant_id, deleted_at=None).first()
        if not gr:
            abort(404, message="Goods receipt not found")
        if gr.status == "completed":
            abort(400, message="Cannot delete a completed goods receipt")
        db.session.delete(gr)
        db.session.commit()
        return {"message": "Deleted"}, 204


@blp.route("/api/v1/goods-receipts/<int:receipt_id>/complete")
class GoodsReceiptComplete(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, receipt_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        gr = GoodsReceipt.query.filter_by(id=receipt_id, tenant_id=tenant_id, deleted_at=None).first()
        if not gr:
            abort(404, message="Goods receipt not found")
        if gr.status != "draft":
            abort(400, message=f"Cannot complete in status '{gr.status}'")
        # Create stock movements for each line
        for line in gr.lines:
            try:
                from backend.plugins.inventory.models import StockMovement, ProductStock
                sm = StockMovement(
                    tenant_id=tenant_id,
                    movement_type="in",
                    product_id=line.product_id,
                    location_id=line.location_id or 1,
                    quantity=line.quantity,
                    reference_type="goods_receipt",
                    reference_id=gr.id,
                )
                db.session.add(sm)
                stock = ProductStock.query.filter_by(
                    tenant_id=tenant_id, product_id=line.product_id,
                    location_id=line.location_id or 1
                ).first()
                if stock:
                    stock.quantity += line.quantity
                else:
                    stock = ProductStock(
                        tenant_id=tenant_id, product_id=line.product_id,
                        location_id=line.location_id or 1,
                        quantity=line.quantity,
                    )
                    db.session.add(stock)
            except ImportError:
                pass
        # Update purchase order quantities
        if gr.purchase_order_id:
            from backend.models.purchase import PurchaseOrder, PurchaseOrderLine
            po = db.session.get(PurchaseOrder, gr.purchase_order_id)
            if po:
                for line in gr.lines:
                    if line.purchase_order_line_id:
                        po_line = db.session.get(PurchaseOrderLine, line.purchase_order_line_id)
                        if po_line:
                            po_line.quantity_received = (po_line.quantity_received or 0) + line.quantity
                po.status = "received"
        gr.status = "completed"
        db.session.commit()
        return gr_to_dict(gr)


def generate_number(tenant_id):
    year = date.today().year
    prefix = f"DDT-{year}"
    last = GoodsReceipt.query.filter(
        GoodsReceipt.tenant_id == tenant_id,
        GoodsReceipt.number.like(f"{prefix}%")
    ).order_by(GoodsReceipt.number.desc()).first()
    if last:
        last_num = int(last.number.split("-")[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    return f"{prefix}-{new_num:05d}"

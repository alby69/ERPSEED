from backend.core.models.base import BaseModel
from backend.extensions import db


class GoodsReceipt(BaseModel):
    __tablename__ = "goods_receipts"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    number = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey("soggetti.id"), nullable=False)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey("purchase_orders.id"), nullable=True)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default="draft")  # draft, completed, cancelled
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))

    supplier = db.relationship("Soggetto")
    purchase_order = db.relationship("PurchaseOrder")
    creator = db.relationship("User")
    tenant = db.relationship("Tenant", backref=db.backref("goods_receipts", lazy="dynamic"))

    __table_args__ = (
        db.UniqueConstraint("tenant_id", "number", name="uq_goods_receipt_tenant_number"),
        db.Index("ix_goods_receipt_tenant_status", "tenant_id", "status"),
    )

    def __repr__(self):
        return f"<GoodsReceipt {self.number}>"


class GoodsReceiptLine(BaseModel):
    __tablename__ = "goods_receipt_lines"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    goods_receipt_id = db.Column(db.Integer, db.ForeignKey("goods_receipts.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    purchase_order_line_id = db.Column(db.Integer, db.ForeignKey("purchase_order_lines.id"), nullable=True)
    description = db.Column(db.String(255))
    quantity = db.Column(db.Float, nullable=False, default=0.0)
    location_id = db.Column(db.Integer, nullable=True)

    goods_receipt = db.relationship("GoodsReceipt", backref="lines")
    product = db.relationship("Product")
    tenant = db.relationship("Tenant", backref=db.backref("goods_receipt_lines", lazy="dynamic"))

    def __repr__(self):
        return f"<GoodsReceiptLine gr={self.goods_receipt_id} product={self.product_id}>"

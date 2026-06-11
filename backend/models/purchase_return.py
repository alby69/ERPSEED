from backend.core.models.base import BaseModel
from backend.extensions import db


class PurchaseReturn(BaseModel):
    __tablename__ = "purchase_returns"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    number = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey("soggetti.id"), nullable=False)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey("purchase_orders.id"), nullable=True)
    goods_receipt_id = db.Column(db.Integer, db.ForeignKey("goods_receipts.id"), nullable=True)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default="draft")
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    reason = db.Column(db.String(255))

    supplier = db.relationship("Soggetto")
    purchase_order = db.relationship("PurchaseOrder")
    goods_receipt = db.relationship("GoodsReceipt")
    creator = db.relationship("User")
    tenant = db.relationship("Tenant", backref=db.backref("purchase_returns", lazy="dynamic"))

    __table_args__ = (
        db.UniqueConstraint("tenant_id", "number", name="uq_purchase_return_tenant_number"),
        db.Index("ix_purchase_return_tenant_status", "tenant_id", "status"),
    )

    def __repr__(self):
        return f"<PurchaseReturn {self.number}>"


class PurchaseReturnLine(BaseModel):
    __tablename__ = "purchase_return_lines"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    purchase_return_id = db.Column(db.Integer, db.ForeignKey("purchase_returns.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    description = db.Column(db.String(255))
    quantity = db.Column(db.Float, nullable=False, default=0.0)
    unit_price = db.Column(db.Float, default=0.0)
    location_id = db.Column(db.Integer, nullable=True)

    purchase_return = db.relationship("PurchaseReturn", backref="lines")
    product = db.relationship("Product")
    tenant = db.relationship("Tenant", backref=db.backref("purchase_return_lines", lazy="dynamic"))

    def __repr__(self):
        return f"<PurchaseReturnLine pr={self.purchase_return_id} product={self.product_id}>"

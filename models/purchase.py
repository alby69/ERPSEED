from .base import BaseModel
from extensions import db
import datetime


class PurchaseOrder(BaseModel):
    __tablename__ = "purchase_orders"

    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True
    )

    number = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, default=datetime.date.today)
    supplier_id = db.Column(db.Integer, db.ForeignKey("soggetti.id"), nullable=False)
    status = db.Column(db.String(20), default="draft")
    total_amount = db.Column(db.Float, default=0)
    expected_date = db.Column(db.Date)
    notes = db.Column(db.Text)

    tenant = db.relationship(
        "Tenant", backref=db.backref("purchase_orders", lazy="dynamic")
    )
    supplier = db.relationship("Soggetto")
    lines = db.relationship(
        "PurchaseOrderLine", back_populates="order", cascade="all, delete-orphan"
    )

    __table_args__ = (db.Index("ix_purchase_tenant_number", "tenant_id", "number"),)


class PurchaseOrderLine(BaseModel):
    __tablename__ = "purchase_order_lines"

    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True
    )

    order_id = db.Column(
        db.Integer, db.ForeignKey("purchase_orders.id"), nullable=False
    )
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    description = db.Column(db.String(255))
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    quantity_received = db.Column(db.Float, default=0)

    tenant = db.relationship("Tenant")
    order = db.relationship("PurchaseOrder", back_populates="lines")
    product = db.relationship("Product")

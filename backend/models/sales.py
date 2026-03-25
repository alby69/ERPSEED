from .base import BaseModel
from backend.extensions import db
import datetime


class SalesOrder(BaseModel):
    __tablename__ = "sales_orders"

    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True
    )

    number = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, default=datetime.date.today)
    customer_id = db.Column(db.Integer, db.ForeignKey("soggetti.id"), nullable=False)
    status = db.Column(db.String(20), default="draft")
    total_amount = db.Column(db.Float, default=0)
    notes = db.Column(db.Text)

    tenant = db.relationship(
        "Tenant", backref=db.backref("sales_orders", lazy="dynamic")
    )
    customer = db.relationship("Soggetto")
    lines = db.relationship(
        "SalesOrderLine", back_populates="order", cascade="all, delete-orphan"
    )

    __table_args__ = (db.Index("ix_order_tenant_number", "tenant_id", "number"),)


class SalesOrderLine(BaseModel):
    __tablename__ = "sales_order_lines"

    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True
    )

    order_id = db.Column(db.Integer, db.ForeignKey("sales_orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    description = db.Column(db.String(255))
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

    tenant = db.relationship("Tenant")
    order = db.relationship("SalesOrder", back_populates="lines")
    product = db.relationship("Product")

from .base import BaseModel
from backend.extensions import db


class Product(BaseModel):
    """Product/Service master data."""

    __tablename__ = "products"

    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True
    )

    name = db.Column(db.String(150), nullable=False, index=True)
    code = db.Column(db.String(50), index=True)
    description = db.Column(db.Text)
    unit_price = db.Column(db.Float)
    category = db.Column(db.String(100))
    sku = db.Column(db.String(50))
    barcode = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    track_inventory = db.Column(db.Boolean, default=False)
    current_stock = db.Column(db.Float, default=0)
    reorder_level = db.Column(db.Float, default=0)
    unit_of_measure = db.Column(db.String(20), default="pcs")
    weight = db.Column(db.Float)
    dimensions = db.Column(db.String(50))

    tenant = db.relationship("Tenant", backref=db.backref("products", lazy="dynamic"))

    __table_args__ = (db.Index("ix_product_tenant_code", "tenant_id", "code"),)

    def __repr__(self):
        return f"<Product {self.name}>"


class ProductStock(BaseModel):
    """Stock tracking for products across warehouses."""

    __tablename__ = "product_stocks"

    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    warehouse_id = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Float, default=0)
    reserved = db.Column(db.Float, default=0)
    available = db.Column(db.Float, default=0)
    location = db.Column(db.String(100))

    product = db.relationship("Product", backref="stocks")

    __table_args__ = (
        db.UniqueConstraint("product_id", "warehouse_id", name="uq_product_warehouse"),
    )

from backend.core.models.base import BaseModel
from backend.extensions import db


class Lot(BaseModel):
    """Lotto di prodotti."""
    __tablename__ = "lots"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    code = db.Column(db.String(100), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey("soggetti.id"), nullable=True)
    quantity = db.Column(db.Float, default=0.0)
    initial_quantity = db.Column(db.Float, default=0.0)
    manufacturing_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    notes = db.Column(db.Text)

    __table_args__ = (
        db.UniqueConstraint("tenant_id", "code", "product_id", name="uq_lot_product"),
    )


class SerialNumber(BaseModel):
    """Serial number tracking."""
    __tablename__ = "serial_numbers"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    code = db.Column(db.String(100), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    lot_id = db.Column(db.Integer, db.ForeignKey("lots.id"), nullable=True)
    status = db.Column(db.String(20), default="available")  # available, reserved, sold, returned, scrapped
    order_id = db.Column(db.Integer, nullable=True)  # sales or purchase order line
    order_type = db.Column(db.String(20))  # sales, purchase
    sold_date = db.Column(db.Date)
    notes = db.Column(db.Text)

    __table_args__ = (
        db.UniqueConstraint("tenant_id", "code", name="uq_serial_number"),
    )

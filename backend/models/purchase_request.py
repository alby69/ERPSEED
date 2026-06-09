from backend.core.models.base import BaseModel
from backend.extensions import db


class PurchaseRequest(BaseModel):
    """Richiesta d'Acquisto interna."""
    __tablename__ = "purchase_requests"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    number = db.Column(db.String(50), nullable=False)
    request_date = db.Column(db.Date, nullable=False)
    required_date = db.Column(db.Date)
    requester_id = db.Column(db.Integer, db.ForeignKey("hr_employees.id"), nullable=True)
    department_id = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), default="draft")  # draft, pending, approved, rejected, ordered
    notes = db.Column(db.Text)

    lines = db.relationship("PurchaseRequestLine", back_populates="request", lazy="joined",
                            cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint("tenant_id", "number", name="uq_purchase_request_number"),
    )


class PurchaseRequestLine(BaseModel):
    __tablename__ = "purchase_request_lines"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey("purchase_requests.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    notes = db.Column(db.String(255))

    request = db.relationship("PurchaseRequest", back_populates="lines")
    product = db.relationship("Product")


class RFQ(BaseModel):
    """Request for Quotation / Richiesta di Preventivo."""
    __tablename__ = "rfqs"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    number = db.Column(db.String(50), nullable=False)
    rfq_date = db.Column(db.Date, nullable=False)
    valid_until = db.Column(db.Date)
    status = db.Column(db.String(20), default="draft")  # draft, sent, received, ordered, cancelled
    purchase_request_id = db.Column(db.Integer, db.ForeignKey("purchase_requests.id"), nullable=True)
    notes = db.Column(db.Text)

    lines = db.relationship("RFQLine", back_populates="rfq", lazy="joined",
                            cascade="all, delete-orphan")
    quotations = db.relationship("SupplierQuotation", back_populates="rfq", lazy="joined")

    __table_args__ = (
        db.UniqueConstraint("tenant_id", "number", name="uq_rfq_number"),
    )


class RFQLine(BaseModel):
    __tablename__ = "rfq_lines"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)
    rfq_id = db.Column(db.Integer, db.ForeignKey("rfqs.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Float, nullable=False)

    rfq = db.relationship("RFQ", back_populates="lines")
    product = db.relationship("Product")


class SupplierQuotation(BaseModel):
    """Preventivo ricevuto da un fornitore in risposta a RFQ."""
    __tablename__ = "supplier_quotations"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    rfq_id = db.Column(db.Integer, db.ForeignKey("rfqs.id"), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey("soggetti.id"), nullable=False)
    quotation_date = db.Column(db.Date, nullable=False)
    valid_until = db.Column(db.Date)
    total_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default="pending")  # pending, accepted, rejected
    notes = db.Column(db.Text)

    lines = db.relationship("SupplierQuotationLine", back_populates="quotation", lazy="joined",
                            cascade="all, delete-orphan")
    rfq = db.relationship("RFQ", back_populates="quotations")


class SupplierQuotationLine(BaseModel):
    __tablename__ = "supplier_quotation_lines"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)
    quotation_id = db.Column(db.Integer, db.ForeignKey("supplier_quotations.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    delivery_date = db.Column(db.Date)

    quotation = db.relationship("SupplierQuotation", back_populates="lines")
    product = db.relationship("Product")

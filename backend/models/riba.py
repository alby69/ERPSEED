from backend.core.models.base import BaseModel
from backend.extensions import db


class RiBa(BaseModel):
    """Ricevuta Bancaria batch."""
    __tablename__ = "riba_batches"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    number = db.Column(db.String(50), nullable=False)
    batch_date = db.Column(db.Date, nullable=False)
    bank_name = db.Column(db.String(200))
    bank_iban = db.Column(db.String(50))
    total_amount = db.Column(db.Float, default=0.0)
    collected_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default="draft")  # draft, sent, partially_collected, collected, rejected
    notes = db.Column(db.Text)

    items = db.relationship("RiBaItem", back_populates="riba", lazy="joined",
                            cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint("tenant_id", "number", name="uq_riba_number"),
    )


class RiBaItem(BaseModel):
    __tablename__ = "riba_items"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    riba_id = db.Column(db.Integer, db.ForeignKey("riba_batches.id"), nullable=False)
    invoice_id = db.Column(db.Integer, nullable=True)
    maturity_id = db.Column(db.Integer, nullable=True)
    soggetto_id = db.Column(db.Integer, db.ForeignKey("soggetti.id"), nullable=False)
    soggetto_name = db.Column(db.String(200))
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default="pending")  # pending, collected, rejected

    riba = db.relationship("RiBa", back_populates="items")

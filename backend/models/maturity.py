from datetime import date
from backend.core.models.base import BaseModel
from backend.extensions import db


class Maturity(BaseModel):
    __tablename__ = "maturities"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    party_id = db.Column(db.Integer, db.ForeignKey("soggetti.id"), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False, default=0.0)
    paid_amount = db.Column(db.Float, default=0.0)
    balance = db.Column(db.Float, default=0.0)
    reference_type = db.Column(db.String(50))  # invoice, journal_entry, etc.
    reference_id = db.Column(db.Integer)
    reference_number = db.Column(db.String(50))
    description = db.Column(db.String(255))
    status = db.Column(db.String(20), default="open")  # open, partial, paid, overdue, cancelled

    party = db.relationship("Soggetto")
    tenant = db.relationship("Tenant", backref=db.backref("maturities", lazy="dynamic"))

    __table_args__ = (
        db.Index("ix_maturity_tenant_status", "tenant_id", "status"),
        db.Index("ix_maturity_tenant_due", "tenant_id", "due_date"),
    )

    def __repr__(self):
        return f"<Maturity {self.id}: {self.party_id} due={self.due_date} balance={self.balance}>"

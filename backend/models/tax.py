from backend.core.models.base import BaseModel
from backend.extensions import db


class TaxRate(BaseModel):
    __tablename__ = "tax_rates"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    code = db.Column(db.String(20), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    rate = db.Column(db.Float, nullable=False, default=0.0)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    valid_from = db.Column(db.Date, nullable=True)
    valid_to = db.Column(db.Date, nullable=True)

    tenant = db.relationship("Tenant", backref=db.backref("tax_rates", lazy="dynamic"))

    __table_args__ = (
        db.UniqueConstraint("tenant_id", "code", name="uq_tax_rate_tenant_code"),
    )

    def __repr__(self):
        return f"<TaxRate {self.code}: {self.rate}%>"

from backend.core.models.base import BaseModel
from backend.extensions import db


class Contract(BaseModel):
    __tablename__ = "contracts"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    number = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    party_id = db.Column(db.Integer, db.ForeignKey("soggetti.id"), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    value = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default="draft")  # draft, active, completed, terminated, cancelled
    notes = db.Column(db.Text)
    auto_renew = db.Column(db.Boolean, default=False)
    renewal_notice_days = db.Column(db.Integer, default=30)

    party = db.relationship("Soggetto")
    tenant = db.relationship("Tenant", backref=db.backref("contracts", lazy="dynamic"))

    __table_args__ = (
        db.UniqueConstraint("tenant_id", "number", name="uq_contract_tenant_number"),
        db.Index("ix_contract_tenant_status", "tenant_id", "status"),
    )

    def __repr__(self):
        return f"<Contract {self.number}: {self.name}>"

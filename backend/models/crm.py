from backend.core.models.base import BaseModel
from backend.extensions import db


class Lead(BaseModel):
    __tablename__ = "crm_leads"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(200))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    source = db.Column(db.String(50))  # website, referral, cold_call, email_campaign, etc.
    status = db.Column(db.String(20), default="new")  # new, contacted, qualified, lost
    notes = db.Column(db.Text)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"))

    assignee = db.relationship("User", foreign_keys=[assigned_to])
    tenant = db.relationship("Tenant", backref=db.backref("crm_leads", lazy="dynamic"))

    __table_args__ = (
        db.Index("ix_crm_lead_tenant_status", "tenant_id", "status"),
    )

    def __repr__(self):
        return f"<Lead {self.first_name} {self.last_name}>"


class Opportunity(BaseModel):
    __tablename__ = "crm_opportunities"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    lead_id = db.Column(db.Integer, db.ForeignKey("crm_leads.id"), nullable=True)
    name = db.Column(db.String(200), nullable=False)
    party_id = db.Column(db.Integer, db.ForeignKey("soggetti.id"), nullable=True)
    expected_revenue = db.Column(db.Float, default=0.0)
    probability = db.Column(db.Integer, default=0)  # 0-100
    stage = db.Column(db.String(30), default="qualification")  # qualification, proposal, negotiation, won, lost
    expected_close_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"))

    lead = db.relationship("Lead", foreign_keys=[lead_id])
    party = db.relationship("Soggetto", foreign_keys=[party_id])
    assignee = db.relationship("User", foreign_keys=[assigned_to])
    tenant = db.relationship("Tenant", backref=db.backref("crm_opportunities", lazy="dynamic"))

    __table_args__ = (
        db.Index("ix_crm_opp_tenant_stage", "tenant_id", "stage"),
    )

    def __repr__(self):
        return f"<Opportunity {self.name}>"

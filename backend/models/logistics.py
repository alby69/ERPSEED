from backend.core.models.base import BaseModel
from backend.extensions import db


class Incoterm(BaseModel):
    """Incoterm (International Commercial Terms) master data."""

    __tablename__ = "incoterms"

    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True
    )
    code = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    tenant = db.relationship("Tenant")

    __table_args__ = (
        db.UniqueConstraint("tenant_id", "code", name="uq_incoterm_tenant_code"),
    )

    def __repr__(self):
        return f"<Incoterm {self.code}>"


class Carrier(BaseModel):
    """Shipping Carrier master data."""

    __tablename__ = "carriers"

    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True
    )
    name = db.Column(db.String(100), nullable=False)
    website = db.Column(db.String(255), nullable=True)
    tracking_url_template = db.Column(db.String(255), nullable=True)

    tenant = db.relationship("Tenant")

    def __repr__(self):
        return f"<Carrier {self.name}>"

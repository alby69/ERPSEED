from backend.core.models.base import BaseModel
from backend.extensions import db


class MovementReason(BaseModel):
    __tablename__ = "movement_reasons"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    code = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    movement_type = db.Column(db.String(20), nullable=False)  # in, out, transfer, adjustment
    is_active = db.Column(db.Boolean, default=True)

    tenant = db.relationship("Tenant", backref=db.backref("movement_reasons", lazy="dynamic"))

    __table_args__ = (
        db.UniqueConstraint("tenant_id", "code", name="uq_movement_reason_tenant_code"),
    )

    def __repr__(self):
        return f"<MovementReason {self.code}>"

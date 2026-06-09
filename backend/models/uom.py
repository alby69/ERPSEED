from backend.core.models.base import BaseModel
from backend.extensions import db


class UnitOfMeasure(BaseModel):
    __tablename__ = "units_of_measure"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    code = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    symbol = db.Column(db.String(10))
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)

    __table_args__ = (
        db.UniqueConstraint("tenant_id", "code", name="uq_uom_tenant_code"),
    )

    def __repr__(self):
        return f"<UnitOfMeasure {self.code}>"

from backend.core.models.base import BaseModel
from backend.extensions import db


class MRPRun(BaseModel):
    """MRP execution run."""
    __tablename__ = "mrp_runs"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    run_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default="completed")  # running, completed, failed
    total_suggestions = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)

    suggestions = db.relationship("MRPSuggestion", back_populates="run", lazy="joined",
                                  cascade="all, delete-orphan")


class MRPSuggestion(BaseModel):
    """MRP suggestion: what to buy or produce."""
    __tablename__ = "mrp_suggestions"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    mrp_run_id = db.Column(db.Integer, db.ForeignKey("mrp_runs.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    suggestion_type = db.Column(db.String(20), nullable=False)  # purchase, produce
    required_quantity = db.Column(db.Float, nullable=False)
    available_quantity = db.Column(db.Float, default=0.0)
    suggested_quantity = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(50))  # sales_order, production_order, forecast
    source_id = db.Column(db.Integer, nullable=True)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(20), default="open")  # open, in_progress, fulfilled, cancelled

    run = db.relationship("MRPRun", back_populates="suggestions")
    product = db.relationship("Product")

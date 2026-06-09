from backend.core.models.base import BaseModel
from backend.extensions import db


class Report(BaseModel):
    """Saved report definition."""
    __tablename__ = "reports"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    code = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), default="general")
    report_type = db.Column(db.String(20), default="list")  # list, summary, chart

    # JSON config: source, columns, filters, group_by, order_by, limit
    config = db.Column(db.JSON, default=dict)

    is_public = db.Column(db.Boolean, default=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    __table_args__ = (
        db.UniqueConstraint("tenant_id", "code", name="uq_report_code"),
    )


class ReportExecution(BaseModel):
    """Report execution history."""
    __tablename__ = "report_executions"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    report_id = db.Column(db.Integer, db.ForeignKey("reports.id"), nullable=False)
    parameters = db.Column(db.JSON, default=dict)
    row_count = db.Column(db.Integer, default=0)
    execution_time_ms = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default="completed")  # completed, failed
    error_message = db.Column(db.Text)
    executed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

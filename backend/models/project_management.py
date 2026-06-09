from datetime import date
from backend.core.models.base import BaseModel
from backend.extensions import db


class BusinessProject(BaseModel):
    """Business project (commessa) for tracking time and budgets."""
    __tablename__ = "business_projects"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    code = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    client_id = db.Column(db.Integer, db.ForeignKey("soggetti.id"), nullable=True)
    manager_id = db.Column(db.Integer, db.ForeignKey("hr_employees.id"), nullable=True)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(20), default="active")  # active, closed, archived
    estimated_hours = db.Column(db.Float, default=0)
    budget_amount = db.Column(db.Float, default=0.0)
    hourly_rate = db.Column(db.Float, default=0.0)

    __table_args__ = (
        db.UniqueConstraint("tenant_id", "code", name="uq_business_project_code"),
    )


class Timesheet(BaseModel):
    __tablename__ = "timesheets"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("hr_employees.id"), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(20), default="draft")  # draft, submitted, approved
    notes = db.Column(db.Text)

    lines = db.relationship("TimesheetLine", back_populates="timesheet", lazy="joined",
                            cascade="all, delete-orphan")


class TimesheetLine(BaseModel):
    __tablename__ = "timesheet_lines"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    timesheet_id = db.Column(db.Integer, db.ForeignKey("timesheets.id"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("business_projects.id"), nullable=True)
    hours = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))

    timesheet = db.relationship("Timesheet", back_populates="lines")

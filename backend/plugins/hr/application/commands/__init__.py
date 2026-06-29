"""
HR Commands - Command classes for HR Agent.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from backend.shared.commands import CreateCommand
from backend.core import capability

@capability(
    name="create_employee",
    description="Onboard a new employee in the company.",
    agent="HRAgent",
    category="hr"
)
@dataclass
class CreateEmployeeCommand(CreateCommand):
    employee_number: str = ""
    first_name: str = ""
    last_name: str = ""
    email: Optional[str] = None
    department_id: Optional[int] = None
    job_title: Optional[str] = None
    hire_date: Optional[str] = None
    employee_type: str = "full-time"
    salary: float = 0.0

@capability(
    name="approve_leave_request",
    description="Approve or reject a pending leave request.",
    agent="HRAgent",
    category="hr"
)
@dataclass
class ApproveLeaveCommand(CreateCommand):
    leave_id: int = 0
    status: str = "approved"
    notes: Optional[str] = None

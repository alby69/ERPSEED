"""
CRM Commands - Command classes for CRM Agent.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from backend.shared.commands import CreateCommand
from backend.core import capability

@capability(
    name="create_lead",
    description="Create a new lead in the CRM.",
    agent="SalesAgent",
    category="crm"
)
@dataclass
class CreateLeadCommand(CreateCommand):
    first_name: str = ""
    last_name: str = ""
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    status: str = "new"
    notes: Optional[str] = None
    assigned_to: Optional[int] = None

@capability(
    name="create_opportunity",
    description="Create a new sales opportunity in the CRM.",
    agent="SalesAgent",
    category="crm"
)
@dataclass
class CreateOpportunityCommand(CreateCommand):
    name: str = ""
    lead_id: Optional[int] = None
    party_id: Optional[int] = None
    expected_revenue: float = 0.0
    probability: int = 0
    stage: str = "qualification"
    expected_close_date: Optional[str] = None
    notes: Optional[str] = None
    assigned_to: Optional[int] = None

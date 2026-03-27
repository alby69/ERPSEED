from dataclasses import dataclass
from typing import Dict, Any, List, Optional

@dataclass
class CreateWorkflowCommand:
    name: str
    description: Optional[str] = None
    trigger_type: str = "record_event"
    project_id: Optional[int] = None
    config: Optional[Dict] = None

@dataclass
class UpdateWorkflowCommand:
    workflow_id: int
    data: Dict[str, Any]

@dataclass
class DeleteWorkflowCommand:
    workflow_id: int

@dataclass
class CreateWebhookCommand:
    name: str
    url: str
    event_type: str
    project_id: Optional[int] = None
    is_active: bool = True

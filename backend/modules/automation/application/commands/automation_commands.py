from dataclasses import dataclass
from typing import Dict, Any, List, Optional

@dataclass
class CreateWorkflowCommand:
    name: str
    description: Optional[str] = None
    trigger_type: str = "record_event"
    projectId: Optional[int] = None
    config: Optional[Dict] = None

@dataclass
class UpdateWorkflowCommand:
    workflowId: int
    data: Dict[str, Any]

@dataclass
class DeleteWorkflowCommand:
    workflowId: int

@dataclass
class CreateWebhookCommand:
    name: str
    url: str
    event_type: str
    projectId: Optional[int] = None
    is_active: bool = True

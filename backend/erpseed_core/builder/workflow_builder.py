"""
Workflow Builder - Creates workflows
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class Transition:
    """Represents a workflow transition"""
    from_state: str
    to_state: str
    action: str = ""
    condition: str = ""
    trigger: str = "manual"


@dataclass
class State:
    """Represents a workflow state"""
    name: str
    type: str = "active"
    permissions: List[str] = field(default_factory=list)


@dataclass
class Workflow:
    """Represents a workflow"""
    name: str
    technical_name: str
    model: str
    title: str = ""
    description: str = ""
    states: List[State] = field(default_factory=list)
    initial_state: str = ""
    transitions: List[Transition] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)


class WorkflowBuilder:
    """Builds workflows from JSON configuration"""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
    
    def build(self, data: Dict[str, Any]) -> Workflow:
        """Build a workflow from JSON data"""
        states = []
        for state_data in data.get("states", []):
            state = State(
                name=state_data["name"],
                type=state_data.get("type", "active"),
                permissions=state_data.get("permissions", []),
            )
            states.append(state)
        
        transitions = []
        for trans_data in data.get("transitions", []):
            trans = Transition(
                from_state=trans_data["from_state"],
                to_state=trans_data["to_state"],
                action=trans_data.get("action", ""),
                condition=trans_data.get("condition", ""),
                trigger=trans_data.get("trigger", "manual"),
            )
            transitions.append(trans)
        
        workflow = Workflow(
            name=data["name"],
            technical_name=data["technical_name"],
            model=data["model"],
            title=data.get("title", data["name"]),
            description=data.get("description", ""),
            states=states,
            initial_state=data.get("initial_state", ""),
            transitions=transitions,
            settings=data.get("settings", {}),
        )
        
        self.workflows[workflow.technical_name] = workflow
        return workflow
    
    def get_workflow(self, technical_name: str) -> Optional[Workflow]:
        """Get a workflow by technical name"""
        return self.workflows.get(technical_name)
    
    def list_workflows(self) -> List[Workflow]:
        """List all built workflows"""
        return list(self.workflows.values())
    
    def to_dict(self, workflow: Workflow) -> Dict[str, Any]:
        """Convert workflow to dictionary"""
        return {
            "name": workflow.name,
            "technical_name": workflow.technical_name,
            "model": workflow.model,
            "title": workflow.title,
            "description": workflow.description,
            "states": [
                {
                    "name": s.name,
                    "type": s.type,
                    "permissions": s.permissions,
                }
                for s in workflow.states
            ],
            "initial_state": workflow.initial_state,
            "transitions": [
                {
                    "from_state": t.from_state,
                    "to_state": t.to_state,
                    "action": t.action,
                    "condition": t.condition,
                    "trigger": t.trigger,
                }
                for t in workflow.transitions
            ],
            "settings": workflow.settings,
        }

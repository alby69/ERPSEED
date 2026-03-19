"""
AI Commands - CQRS Commands for AI operations.
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from backend.shared.commands import Command, QueryCommand


@dataclass
class SendMessageCommand(Command):
    project_id: int = 0; user_id: int = 0; message: str = ""
    conversation_id: Optional[int] = None; context: Dict[str, Any] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SendMessageCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id", 0), metadata=data.get("metadata", {}),
            project_id=data.get("project_id", 0), message=data.get("message", ""),
            conversation_id=data.get("conversation_id"), context=data.get("context"))


@dataclass
class GenerateConfigCommand(Command):
    project_id: int = 0; user_id: int = 0; user_request: str = ""; apply_immediately: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GenerateConfigCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id", 0), metadata=data.get("metadata", {}),
            project_id=data.get("project_id", 0), user_request=data.get("user_request", ""),
            apply_immediately=data.get("apply_immediately", False))


@dataclass
class CreateWorkflowCommand(Command):
    project_id: int = 0; user_id: int = 0; workflow_description: str = ""; trigger_event: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CreateWorkflowCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id", 0), metadata=data.get("metadata", {}),
            project_id=data.get("project_id", 0), workflow_description=data.get("workflow_description", ""),
            trigger_event=data.get("trigger_event"))


@dataclass
class CreateUIViewCommand(Command):
    project_id: int = 0; user_id: int = 0; model_id: int = 0; view_description: str = ""; view_type: str = "list"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CreateUIViewCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id", 0), metadata=data.get("metadata", {}),
            project_id=data.get("project_id", 0), model_id=data.get("model_id", 0),
            view_description=data.get("view_description", ""), view_type=data.get("view_type", "list"))


@dataclass
class GenerateTestSuiteCommand(Command):
    project_id: int = 0; user_id: int = 0; model_name: str = ""; test_description: str = ""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GenerateTestSuiteCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id", 0), metadata=data.get("metadata", {}),
            project_id=data.get("project_id", 0), model_name=data.get("model_name", ""),
            test_description=data.get("test_description", ""))


@dataclass
class GetConversationHistoryQuery(QueryCommand):
    conversation_id: int = 0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GetConversationHistoryQuery":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id", 0), metadata=data.get("metadata", {}),
            entity_id=data.get("conversation_id", 0))


@dataclass
class GetProjectContextQuery(QueryCommand):
    project_id: int = 0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GetProjectContextQuery":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id", 0), metadata=data.get("metadata", {}),
            entity_id=data.get("project_id", 0))


@dataclass
class GetToolDefinitionsQuery(QueryCommand):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GetToolDefinitionsQuery":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id", 0), metadata=data.get("metadata", {}))

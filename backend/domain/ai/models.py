"""
Domain Models for AI.

Pure Python dataclasses for AI conversation and tool management.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List


@dataclass
class ConversationMessage:
    id: Optional[int] = None; role: str = "user"; content: str = ""
    tool_calls: List[Dict] = field(default_factory=list); tool_results: List[Dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "role": self.role, "content": self.content,
            "tool_calls": self.tool_calls, "tool_results": self.tool_results,
            "created_at": self.created_at.isoformat() if self.created_at else None}


@dataclass
class Conversation:
    id: Optional[int] = None; project_id: int = 0; user_id: int = 0
    messages: List[ConversationMessage] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict); status: str = "active"
    created_at: datetime = field(default_factory=datetime.utcnow); updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "project_id": self.project_id, "user_id": self.user_id,
            "messages": [m.to_dict() if hasattr(m, 'to_dict') else m for m in self.messages],
            "context": self.context, "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None}


@dataclass
class ToolDefinition:
    name: str = ""; description: str = ""; parameters: Dict[str, Any] = field(default_factory=dict)
    category: str = "general"; is_enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "description": self.description, "parameters": self.parameters,
            "category": self.category, "is_enabled": self.is_enabled}


@dataclass
class ToolExecution:
    id: Optional[int] = None; tool_name: str = ""; arguments: Dict[str, Any] = field(default_factory=dict)
    result: Any = None; error: Optional[str] = None; execution_time_ms: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "tool_name": self.tool_name, "arguments": self.arguments,
            "result": self.result, "error": self.error, "execution_time_ms": self.execution_time_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None}

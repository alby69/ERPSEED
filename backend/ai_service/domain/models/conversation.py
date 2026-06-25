"""
Conversation Model - Domain model for AI conversations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class Conversation:
    """Represents an AI conversation session."""

    id: Optional[int] = None
    project_id: int = 0
    user_id: int = 0
    title: str = ""
    messages: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, role: str, content: str, **kwargs):
        """Add a message to the conversation."""
        self.messages.append(
            {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
                **kwargs,
            }
        )
        self.updated_at = datetime.utcnow()

    def get_messages(self) -> List[Dict[str, Any]]:
        """Get all messages."""
        return self.messages

    def clear(self):
        """Clear all messages."""
        self.messages = []
        self.updated_at = datetime.utcnow()


@dataclass
class Message:
    """Represents a single message in a conversation."""

    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tool_calls: List[Dict] = None
    tool_call_id: str = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "tool_calls": self.tool_calls,
            "tool_call_id": self.tool_call_id,
        }


@dataclass
class ConversationContext:
    """Context for building AI prompts."""

    project_id: int
    project_name: str = ""
    models: List[Dict[str, Any]] = field(default_factory=list)
    workflows: List[Dict[str, Any]] = field(default_factory=list)
    recent_conversations: List[Dict] = field(default_factory=list)
    custom_instructions: str = ""

    def to_prompt(self) -> str:
        """Convert context to prompt string."""
        parts = []

        if self.project_name:
            parts.append(f"Project: {self.project_name}")

        if self.models:
            model_names = [m.get("name", m.get("table")) for m in self.models]
            parts.append(f"Available models: {', '.join(model_names)}")

        if self.workflows:
            wf_names = [w.get("name") for w in self.workflows]
            parts.append(f"Active workflows: {', '.join(wf_names)}")

        if self.custom_instructions:
            parts.append(f"\nCustom instructions: {self.custom_instructions}")

        return "\n".join(parts)

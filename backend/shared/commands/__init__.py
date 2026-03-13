"""
Command Base Classes - Base classes for all commands in the system.

A Command represents an intention to perform an action. Commands are
immutable and contain all data needed to execute an action.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime
import uuid


@dataclass
class Command:
    """Base class for all commands."""
    
    command_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tenant_id: Optional[int] = None
    user_id: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert command to dictionary."""
        return {
            "command_id": self.command_id,
            "timestamp": self.timestamp.isoformat(),
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "metadata": self.metadata,
        }


@dataclass
class CreateCommand(Command):
    """Base class for create commands."""
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UpdateCommand(Command):
    """Base class for update commands."""
    entity_id: int = 0
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeleteCommand(Command):
    """Base class for delete commands."""
    entity_id: int = 0


@dataclass
class QueryCommand(Command):
    """Base class for query commands."""
    filters: Dict[str, Any] = field(default_factory=dict)
    pagination: Dict[str, Any] = field(default_factory=dict)
    sorting: Dict[str, Any] = field(default_factory=dict)

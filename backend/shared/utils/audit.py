"""
Audit utilities.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
import json


@dataclass
class AuditEntry:
    """Represents an audit log entry."""

    userId: Optional[int] = None
    model_name: str = ""
    record_id: Optional[int] = None
    action: str = ""
    changes: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "userId": self.userId,
            "model_name": self.model_name,
            "record_id": self.record_id,
            "action": self.action,
            "changes": json.dumps(self.changes, default=str) if self.changes else None,
            "timestamp": self.timestamp.isoformat(),
        }


def create_audit_entry(
    userId: Optional[int],
    model_name: str,
    record_id: Optional[int],
    action: str,
    changes: Optional[Dict[str, Any]] = None,
) -> AuditEntry:
    """Create an audit entry.

    Args:
        userId: ID of user performing action
        model_name: Name of the model being modified
        record_id: ID of the record
        action: Action type (create, update, delete, etc.)
        changes: Dictionary of field changes

    Returns:
        AuditEntry instance
    """
    return AuditEntry(
        userId=userId,
        model_name=model_name,
        record_id=record_id,
        action=action,
        changes=changes,
    )

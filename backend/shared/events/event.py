"""
Domain Event - Base event class for event-driven architecture.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
import uuid


@dataclass
class DomainEvent:
    """Base class for all domain events."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    occurred_on: datetime = field(default_factory=datetime.utcnow)
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.event_type:
            self.event_type = self.__class__.__name__


@dataclass
class EntityCreatedEvent(DomainEvent):
    """Event fired when an entity is created."""

    entity_type: str = ""
    entity_id: Optional[int] = None


@dataclass
class EntityUpdatedEvent(DomainEvent):
    """Event fired when an entity is updated."""

    entity_type: str = ""
    entity_id: Optional[int] = None
    changes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EntityDeletedEvent(DomainEvent):
    """Event fired when an entity is deleted."""

    entity_type: str = ""
    entity_id: Optional[int] = None


@dataclass
class UserCreatedEvent(DomainEvent):
    """Event fired when a user is created."""

    user_id: int = 0
    username: str = ""


@dataclass
class UserLoggedInEvent(DomainEvent):
    """Event fired when a user logs in."""

    user_id: int = 0
    username: str = ""

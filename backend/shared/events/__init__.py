"""
Events Package - Event-driven communication infrastructure.
"""

from .event import (
    DomainEvent,
    EntityCreatedEvent,
    EntityUpdatedEvent,
    EntityDeletedEvent,
)
from .event import UserCreatedEvent, UserLoggedInEvent
from .event_bus import EventBus, get_event_bus

__all__ = [
    "DomainEvent",
    "EntityCreatedEvent",
    "EntityUpdatedEvent",
    "EntityDeletedEvent",
    "UserCreatedEvent",
    "UserLoggedInEvent",
    "EventBus",
    "get_event_bus",
]

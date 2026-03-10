"""
Events package for the shared infrastructure layer.
Exports the main DomainEvent and EventBus classes.
"""
from .event import DomainEvent
from .event_bus import EventBus, get_event_bus

__all__ = [
    "DomainEvent", "EventBus", "get_event_bus"
]
"""
Event Bus - In-memory event dispatcher for domain events.
"""

from typing import Callable, Dict, List, Any
from collections import defaultdict
import logging
import threading

from .event import DomainEvent

logger = logging.getLogger(__name__)


class EventBus:
    """In-memory event bus for publishing and subscribing to domain events."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._global_handlers: List[Callable] = []
        self._initialized = True
        logger.info("EventBus initialized")

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe a handler to a specific event type.

        Args:
            event_type: The type of event to listen for
            handler: Callback function to execute when event is published
        """
        self._handlers[event_type].append(handler)
        logger.debug(f"Handler subscribed to {event_type}")

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Unsubscribe a handler from an event type.

        Args:
            event_type: The event type
            handler: The handler to remove
        """
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
                logger.debug(f"Handler unsubscribed from {event_type}")
            except ValueError:
                pass

    def subscribe_global(self, handler: Callable) -> None:
        """Subscribe a handler to all events.

        Args:
            handler: Callback function executed for every event
        """
        self._global_handlers.append(handler)

    def publish(self, event: DomainEvent) -> None:
        """Publish an event to all subscribed handlers.

        Args:
            event: The domain event to publish
        """
        event_type = event.event_type

        logger.debug(f"Publishing event: {event_type}")

        for handler in self._handlers.get(event_type, []):
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type}: {e}")

        for handler in self._global_handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in global event handler: {e}")

    def clear(self) -> None:
        """Clear all subscriptions."""
        self._handlers.clear()
        self._global_handlers.clear()
        logger.info("All event subscriptions cleared")

    def get_subscribers(self, event_type: str) -> List[Callable]:
        """Get list of subscribers for an event type.

        Args:
            event_type: The event type

        Returns:
            List of handler functions
        """
        return self._handlers.get(event_type, [])


_event_bus = None


def get_event_bus() -> EventBus:
    """Get the global EventBus instance."""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus

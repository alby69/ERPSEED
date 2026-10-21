"""
EventBus module for internal event-driven communication using in-memory routing and optional Redis Pub/Sub.
"""
import json
import logging
from collections import defaultdict
from typing import Callable, Dict, List, Optional, Any

from backend.shared.events.event import DomainEvent

logger = logging.getLogger(__name__)


class EventBus:
    """
    Event bus implementation supporting in-memory event dispatching and
    optional Redis Pub/Sub for cross-process decoupled event propagation.
    """

    def __init__(self, redis_client=None):
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)
        self.redis_client = redis_client
        logger.info("Core EventBus initialized.")

    def set_redis_client(self, redis_client):
        """Configure or update Redis client instance for Pub/Sub."""
        self.redis_client = redis_client

    def subscribe(self, event_type: str, handler: Callable):
        """
        Subscribes a callback handler to an event type.
        """
        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)
            handler_name = getattr(handler, "__name__", handler.__class__.__name__)
            logger.debug(f"Handler {handler_name} subscribed to event '{event_type}'")

    def publish(self, event: DomainEvent):
        """
        Publishes a domain event to all subscribed local handlers and,
        if available, publishes to Redis Pub/Sub channel.
        """
        event_type = event.event_type
        logger.debug(f"Publishing event '{event_type}' with payload: {event.payload}")

        # Local in-memory handlers execution
        if event_type in self._handlers:
            for handler in list(self._handlers[event_type]):
                handler_name = getattr(handler, "__name__", handler.__class__.__name__)
                try:
                    handler(event)
                    logger.debug(f"Handler {handler_name} executed for event '{event_type}'")
                except Exception as e:
                    logger.error(
                        f"Error executing handler {handler_name} for event '{event_type}': {e}",
                        exc_info=True
                    )

        # Redis Pub/Sub integration if configured
        if self.redis_client:
            try:
                channel = f"events:{event_type}"
                event_data = {
                    "event_type": event_type,
                    "payload": event.payload
                }
                self.redis_client.publish(channel, json.dumps(event_data))
                logger.debug(f"Event '{event_type}' published to Redis channel '{channel}'")
            except Exception as e:
                logger.warning(f"Failed to publish event '{event_type}' to Redis: {e}")

    def unsubscribe(self, event_type: str, handler: Callable):
        """
        Unsubscribes a callback handler from an event type.
        """
        if event_type in self._handlers and handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            handler_name = getattr(handler, "__name__", handler.__class__.__name__)
            logger.debug(f"Handler {handler_name} unsubscribed from event '{event_type}'")


# Global singleton instance
_core_event_bus = EventBus()


def get_event_bus() -> EventBus:
    """Returns the global EventBus instance."""
    return _core_event_bus

"""
Example Plugin - Example implementation using the new plugin system.

This demonstrates how to create a plugin using the new standardized interface.
"""

from backend.plugin_system.interfaces import Plugin
from typing import List, Dict, Any
from flask import Flask
from backend.container import ServiceContainer
import logging

logger = logging.getLogger(__name__)


class ExamplePlugin(Plugin):
    """
    Example plugin demonstrating the new, simplified plugin interface.
    """

    @property
    def name(self) -> str:
        return "example"

    @property
    def version(self) -> str:
        return "1.0.0"

    def register(self, app: Flask, container: ServiceContainer):
        """
        Called when the plugin is loaded.
        Use this to register blueprints, services, event handlers, etc.
        """
        logger.info(f"Registering {self.name} plugin v{self.version}")
        
        # Example: subscribe to an event
        event_bus = container.get('event_bus')
        if event_bus:
            event_bus.subscribe("user.created", self.on_user_created)

    def unregister(self, app: Flask):
        """
        Called when the plugin is unloaded.
        Use this to clean up resources.
        """
        logger.info(f"Unregistering {self.name} plugin")

    def on_user_created(self, event):
        """Handle user created event."""
        logger.info(f"ExamplePlugin received event: {event.event_type} with payload: {event.payload}")

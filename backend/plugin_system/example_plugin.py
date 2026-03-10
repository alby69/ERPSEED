"""
Example Plugin - Example implementation using the new plugin system.

This demonstrates how to create a plugin using the new standardized interface.
"""

from backend.plugin_system.interfaces import Plugin, PluginMetadata
from typing import List, Dict, Any


class ExamplePlugin(Plugin):
    """
    Example plugin demonstrating the new plugin interface.
    """

    metadata = PluginMetadata(
        name="example",
        version="1.0.0",
        description="An example plugin for FlaskERP",
        author="FlaskERP Team",
        icon="star",
        category="examples",
        tags=["example", "demo"],
        dependencies=[],
        core_version_min="1.0.0",
    )

    def __init__(self, app=None, db=None, api=None):
        super().__init__(app, db, api)
        self._config = {}

    def install(self, app, db) -> None:
        """Install the plugin."""
        logger = (
            app.logger
            if hasattr(app, "logger")
            else __import__("logging").getLogger(__name__)
        )
        logger.info(f"Installing {self.name} plugin")

        self._initialized = True

    def uninstall(self) -> None:
        """Uninstall the plugin."""
        logger = __import__("logging").getLogger(__name__)
        logger.info(f"Uninstalling {self.name} plugin")

        self._enabled = False
        self._initialized = False

    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the plugin."""
        self._config = config

    def get_routes(self) -> List[Dict[str, Any]]:
        """Get API routes."""
        return [
            {
                "path": "/example",
                "name": "example_bp",
                "description": "Example plugin endpoint",
            }
        ]

    def get_menu_items(self) -> List[Dict[str, Any]]:
        """Get menu items."""
        return [
            {
                "id": "example",
                "label": "Example",
                "icon": "star",
                "path": "/example",
                "menu_position": 999,
            }
        ]

    def on_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Handle domain events."""
        logger = __import__("logging").getLogger(__name__)
        logger.info(f"{self.name} received event: {event_type}")

    def subscribe_to_events(self) -> List[tuple]:
        """Subscribe to events."""
        return [
            ("user.created", self._on_user_created),
            ("record.created", self._on_record_created),
        ]

    def _on_user_created(self, event):
        """Handle user created event."""
        pass

    def _on_record_created(self, event):
        """Handle record created event."""
        pass


# Per registrazione automatica
def get_plugin_class():
    return ExamplePlugin

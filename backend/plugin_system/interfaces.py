"""
Plugin Interface - Standard interface for FlaskERP plugins.

This module defines the abstract base class that all plugins must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Flask
    from flask_smorest import Api


@dataclass
class PluginMetadata:
    """Plugin metadata information."""

    name: str
    version: str
    description: str
    author: str = ""
    license: str = "MIT"
    icon: str = "box"
    category: str = "general"
    tags: List[str] = None
    homepage: str = ""
    core_version_min: str = "1.0.0"
    dependencies: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.dependencies is None:
            self.dependencies = []


class Plugin(ABC):
    """
    Abstract base class for FlaskERP plugins.

    All plugins must inherit from this class and implement the required methods.

    Usage:
        class MyPlugin(Plugin):
            name = "my_plugin"
            version = "1.0.0"
            description = "My custom plugin"

            def install(self, app, db):
                # Setup
                pass

            def uninstall(self):
                # Cleanup
                pass
    """

    metadata: PluginMetadata

    def __init__(self, app: "Flask" = None, db=None, api: "Api" = None):
        """
        Initialize the plugin.

        Args:
            app: Flask application instance
            db: SQLAlchemy database instance
            api: Flask-smorest API instance
        """
        self.app = app
        self.db = db
        self.api = api
        self._enabled = False
        self._initialized = False

    @property
    def name(self) -> str:
        """Plugin unique identifier."""
        return (
            self.metadata.name if hasattr(self, "metadata") else self.__class__.__name__
        )

    @property
    def version(self) -> str:
        """Plugin version."""
        return getattr(self, "__version__", "1.0.0")

    @property
    def enabled(self) -> bool:
        """Check if plugin is enabled."""
        return self._enabled

    @property
    def initialized(self) -> bool:
        """Check if plugin has been initialized."""
        return self._initialized

    @abstractmethod
    def install(self, app: "Flask", db) -> None:
        """
        Install the plugin.

        Called when plugin is first installed or enabled.
        Register blueprints, routes, models, etc. here.

        Args:
            app: Flask application instance
            db: SQLAlchemy database instance
        """
        pass

    @abstractmethod
    def uninstall(self) -> None:
        """
        Uninstall the plugin.

        Called when plugin is disabled or removed.
        Clean up resources here.
        """
        pass

    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure the plugin.

        Called with plugin-specific configuration.

        Args:
            config: Configuration dictionary
        """
        pass

    def get_routes(self) -> List[Dict[str, Any]]:
        """
        Get plugin API routes.

        Returns:
            List of route definitions
        """
        return []

    def get_menu_items(self) -> List[Dict[str, Any]]:
        """
        Get menu items for the plugin.

        Returns:
            List of menu item dictionaries
        """
        return []

    def get_widgets(self) -> List[Dict[str, Any]]:
        """
        Get dashboard widgets.

        Returns:
            List of widget definitions
        """
        return []

    def get_permissions(self) -> List[Dict[str, Any]]:
        """
        Get permissions defined by this plugin.

        Returns:
            List of permission definitions
        """
        return []

    def on_startup(self) -> None:
        """Called when application starts."""
        pass

    def on_shutdown(self) -> None:
        """Called when application shuts down."""
        pass

    def on_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Handle a domain event.

        Args:
            event_type: Type of event
            event_data: Event payload
        """
        pass

    def subscribe_to_events(self) -> List[tuple]:
        """
        Subscribe to domain events.

        Returns:
            List of (event_type, handler_function) tuples
        """
        return []

    def health_check(self) -> Dict[str, Any]:
        """
        Check plugin health status.

        Returns:
            Dictionary with health status
        """
        return {
            "name": self.name,
            "enabled": self.enabled,
            "initialized": self.initialized,
            "status": "healthy" if self._enabled else "disabled",
        }


class PluginMixin:
    """
    Mixin class to add plugin support to Flask app.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._plugin_manager = None

    @property
    def plugin_manager(self):
        """Get the plugin manager."""
        return self._plugin_manager

    def init_plugin_manager(self, db=None, api=None):
        """Initialize the plugin manager."""
        from .manager import PluginManager

        self._plugin_manager = PluginManager(self, db, api)
        return self._plugin_manager

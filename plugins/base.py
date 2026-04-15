"""
Plugin Architecture Base Classes.

This module provides the base classes for implementing plugins in FlaskERP.
Plugins allow extending the system with new functionality without modifying the core.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class BasePlugin(ABC):
    """
    Base class for all plugins with multi-tenant support.

    Attributes:
        name: Unique identifier for the plugin.
        version: Plugin version string.
        description: Human-readable description.
        icon: Icon name for UI.
        dependencies: List of other plugin names required by this plugin.
        is_free: Whether the module is free or premium.
        price: Price for premium modules.
        plan_required: Minimum plan required to use this module.
    """

    # Metadata
    name: str = "base_plugin"
    version: str = "1.0.0"
    description: str = "Base plugin"
    icon: str = "box"

    # Licensing
    is_free: bool = True
    price: Optional[float] = None
    plan_required: str = "starter"

    # Dependencies
    dependencies: List[str] = []
    core_version_min: str = "1.0.0"

    def __init__(self, app=None, db=None, api=None):
        """
        Initialize the plugin.

        Args:
            app: Flask application instance.
            db: SQLAlchemy database instance.
            api: Flask-smorest API instance.
        """
        self.app = app
        self.db = db
        self.api = api
        self._enabled = False

    @property
    def enabled(self) -> bool:
        """Check if plugin is enabled."""
        return self._enabled

    # === Metodi Obbligatori ===

    @abstractmethod
    def register(self):
        """
        Register the plugin's resources (blueprints, routes, etc.).
        This is called when the plugin is installed/enabled.
        """
        pass

    @abstractmethod
    def init_db(self):
        """
        Initialize plugin-specific database models.
        This is called during app initialization.
        """
        pass

    # === Lifecycle ===

    def install(self):
        """
        Run installation tasks.
        Called when plugin is first installed.
        """
        self._enabled = True
        self.register()
        self.init_db()

    def uninstall(self):
        """
        Run uninstallation tasks.
        Called when plugin is uninstalled.
        """
        self._enabled = False

    # === Hook Opzionali ===

    def before_request(self, tenant_id: int):
        """
        Hook called before each request.

        Args:
            tenant_id: Current tenant ID.
        """
        pass

    def after_request(self, response, tenant_id: int):
        """
        Hook called after each request.

        Args:
            response: Flask response object.
            tenant_id: Current tenant ID.

        Returns:
            Modified response object.
        """
        return response

    def on_enable(self, tenant_id: int, config: dict):
        """
        Called when tenant enables module.

        Args:
            tenant_id: Tenant ID that enabled the module.
            config: Module configuration for this tenant.
        """
        pass

    def on_disable(self, tenant_id: int):
        """
        Called when tenant disables module.

        Args:
            tenant_id: Tenant ID that disabled the module.
        """
        pass

    # === Event Hooks ===

    def on_event(self, event_type: str, event_data: dict):
        """
        Hook called when an event is published.

        Args:
            event_type: Type of event (e.g., 'record.created')
            event_data: Event payload data
        """
        pass

    def subscribe_to_events(self, event_bus) -> list:
        """
        Subscribe to domain events.

        Args:
            event_bus: The EventBus instance

        Returns:
            List of (event_type, handler) tuples to subscribe
        """
        return []

    # === UI Hooks ===

    def get_menu_items(self, tenant_id: int) -> List[dict]:
        """
        Restituisce voci di menu per il modulo.

        Args:
            tenant_id: Current tenant ID.

        Returns:
            List of menu item dictionaries.
            Format: [
                {
                    'id': 'moduleId',
                    'label': 'Label',
                    'icon': 'icon-name',
                    'path': '/path',
                    'menu_position': 100,
                    'children': [...]  # optional sub-items
                }
            ]
        """
        return []

    def get_widgets(self, tenant_id: int) -> List[dict]:
        """
        Restituisce widget per la dashboard.

        Args:
            tenant_id: Current tenant ID.

        Returns:
            List of widget dictionaries.
            Format: [
                {
                    'id': 'widget_id',
                    'type': 'chart|table|text',
                    'title': 'Widget Title',
                    'size': 'small|medium|large',
                    'config': {...}
                }
            ]
        """
        return []

    def get_api_routes(self) -> List[str]:
        """
        Restituisce rotte API esposte.

        Returns:
            List of API route paths.
        """
        return []

    # === Licensing ===

    def validate_license(self, license_key: str, tenant_id: int) -> bool:
        """
        Valida licenza per modulo premium.

        Args:
            license_key: License key to validate.
            tenant_id: Tenant requesting validation.

        Returns:
            True if valid, False otherwise.
        """
        return True

    # === Info ===

    def get_info(self) -> Dict[str, Any]:
        """
        Get plugin information.

        Returns:
            Dictionary with plugin metadata.
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "icon": self.icon,
            "dependencies": self.dependencies,
            "is_free": self.is_free,
            "price": self.price,
            "plan_required": self.plan_required,
            "enabled": self.enabled,
        }


class PluginMixin:
    """
    Mixin class to add plugin support to Flask app.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._plugin_registry = {}

    @property
    def plugins(self):
        """Get all registered plugins."""
        return self._plugin_registry

    def register_plugin(self, plugin: BasePlugin):
        """
        Register a plugin with the application.

        Args:
            plugin: Plugin instance to register.
        """
        self._plugin_registry[plugin.name] = plugin

    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """
        Get a registered plugin by name.

        Args:
            name: Plugin name.

        Returns:
            Plugin instance or None if not found.
        """
        return self._plugin_registry.get(name)

    def enable_plugin(self, name: str) -> bool:
        """
        Enable a registered plugin.

        Args:
            name: Plugin name.

        Returns:
            True if enabled successfully, False otherwise.
        """
        plugin = self.get_plugin(name)
        if plugin and not plugin.enabled:
            plugin.install()
            return True
        return False

    def disable_plugin(self, name: str) -> bool:
        """
        Disable a registered plugin.

        Args:
            name: Plugin name.

        Returns:
            True if disabled successfully, False otherwise.
        """
        plugin = self.get_plugin(name)
        if plugin and plugin.enabled:
            plugin.uninstall()
            return True
        return False

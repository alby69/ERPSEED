"""
Plugin Registry - Manages plugin lifecycle and discovery.
"""

from typing import Dict, List, Optional, Type
import importlib
import os

from .base import BasePlugin


class ModuleRegistry:
    """
    Central registry for managing plugins.
    Handles plugin discovery, loading, enabling, and disabling.
    """

    _plugins: Dict[str, BasePlugin] = {}
    _plugin_classes: Dict[str, Type[BasePlugin]] = {}
    _enabled_plugins: List[str] = []

    @classmethod
    def register(cls, plugin_class: Type[BasePlugin], name: str = None):
        """
        Register a plugin class.

        Args:
            plugin_class: Plugin class to register.
            name: Optional name override.
        """
        plugin_name = name or plugin_class.name
        cls._plugin_classes[plugin_name] = plugin_class

    @classmethod
    def get(cls, name: str) -> Optional[BasePlugin]:
        """
        Get an instantiated plugin by name.

        Args:
            name: Plugin name.

        Returns:
            Plugin instance or None.
        """
        return cls._plugins.get(name)

    @classmethod
    def get_all(cls) -> Dict[str, BasePlugin]:
        """Get all registered plugins."""
        return cls._plugins.copy()

    @classmethod
    def get_enabled(cls) -> List[BasePlugin]:
        """Get all enabled plugins."""
        return [p for p in cls._plugins.values() if p.enabled]

    @classmethod
    def enable(cls, name: str, app=None, db=None, api=None) -> bool:
        """
        Enable a plugin.

        Args:
            name: Plugin name to enable.
            app: Flask application instance.
            db: SQLAlchemy database instance.
            api: Flask-smorest API instance.

        Returns:
            True if enabled successfully.
        """
        if name in cls._plugins and cls._plugins[name].enabled:
            return True

        if name not in cls._plugin_classes:
            raise ValueError(f"Plugin '{name}' not registered")

        plugin_class = cls._plugin_classes[name]
        plugin = plugin_class(app=app, db=db, api=api)

        cls._plugins[name] = plugin
        cls._enabled_plugins.append(name)

        plugin.install()
        return True

    @classmethod
    def disable(cls, name: str) -> bool:
        """
        Disable a plugin.

        Args:
            name: Plugin name to disable.

        Returns:
            True if disabled successfully.
        """
        if name not in cls._plugins:
            return False

        cls._plugins[name].uninstall()
        del cls._plugins[name]

        if name in cls._enabled_plugins:
            cls._enabled_plugins.remove(name)

        return True

    @classmethod
    def init_app(cls, app, api, db):
        """
        Initialize all enabled plugins with app context.

        Args:
            app: Flask application.
            api: Flask-smorest API.
            db: SQLAlchemy database.
        """
        for name in cls._enabled_plugins:
            if name in cls._plugins:
                plugin = cls._plugins[name]
                plugin.app = app
                plugin.db = db
                plugin.api = api

    @classmethod
    def discover_plugins(cls, plugins_dir: str):
        """
        Auto-discover plugins in a directory.

        Args:
            plugins_dir: Path to plugins directory.
        """
        if not os.path.exists(plugins_dir):
            return

        for item in os.listdir(plugins_dir):
            item_path = os.path.join(plugins_dir, item)
            if os.path.isdir(item_path) and not item.startswith("_"):
                cls._discover_plugin(item, item_path)

    @classmethod
    def _discover_plugin(cls, name: str, path: str):
        """
        Discover a single plugin from its directory.

        Args:
            name: Plugin name.
            path: Plugin directory path.
        """
        plugin_file = os.path.join(path, "plugin.py")
        if os.path.exists(plugin_file):
            module_name = f"backend.plugins.{name}.plugin"
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, "get_plugin"):
                    plugin_class = module.get_plugin()
                    if plugin_class:
                        cls.register(plugin_class)
            except ImportError as e:
                print(f"Failed to import plugin {name}: {e}")

    @classmethod
    def list_plugins(cls) -> List[Dict]:
        """
        Get list of all plugins with their status.

        Returns:
            List of plugin info dictionaries.
        """
        result = []

        for name, plugin_class in cls._plugin_classes.items():
            info = {
                "name": name,
                "class": plugin_class.__name__,
                "enabled": name in cls._enabled_plugins,
            }
            result.append(info)

        return result


def register_plugin(plugin_class: Type[BasePlugin]):
    """
    Decorator to register a plugin class.

    Usage:
        @register_plugin
        class MyPlugin(BasePlugin):
            name = "my_plugin"
            ...
    """
    ModuleRegistry.register(plugin_class)
    return plugin_class


# Backward compatibility alias
PluginRegistry = ModuleRegistry

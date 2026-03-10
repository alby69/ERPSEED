"""
Plugin Manager - Manages plugin lifecycle and discovery.
"""

import logging
import importlib
import os
from typing import Dict, List, Any, Optional, Type
from pathlib import Path

from .interfaces import Plugin, PluginMetadata

logger = logging.getLogger(__name__)


class PluginManager:
    """
    Manages plugin lifecycle: discovery, installation, loading, and卸载.
    """
    
    def __init__(self, app=None, db=None, api=None):
        self.app = app
        self.db = db
        self.api = api
        self._plugins: Dict[str, Plugin] = {}
        self._plugin_classes: Dict[str, Type[Plugin]] = {}
        self._enabled_plugins: List[str] = []
        self._event_bus = None
    
    @property
    def plugins(self) -> Dict[str, Plugin]:
        """Get all registered plugins."""
        return self._plugins
    
    @property
    def enabled_plugins(self) -> List[str]:
        """Get list of enabled plugin names."""
        return self._enabled_plugins
    
    def set_event_bus(self, event_bus) -> None:
        """Set the event bus for plugin communication."""
        self._event_bus = event_bus
    
    def register_plugin_class(self, plugin_class: Type[Plugin]) -> None:
        """
        Register a plugin class.
        
        Args:
            plugin_class: Plugin class to register
        """
        if not issubclass(plugin_class, Plugin):
            raise TypeError(f"{plugin_class} must inherit from Plugin")
        
        name = plugin_class.metadata.name if hasattr(plugin_class, 'metadata') else plugin_class.__name__
        self._plugin_classes[name] = plugin_class
        logger.info(f"Registered plugin class: {name}")
    
    def discover_plugins(self, plugin_dir: str = None) -> List[str]:
        """
        Discover plugins in a directory.
        
        Args:
            plugin_dir: Directory to scan for plugins
            
        Returns:
            List of discovered plugin names
        """
        discovered = []
        
        if plugin_dir is None:
            plugin_dir = os.path.join(os.path.dirname(__file__), "..", "plugins")
        
        plugin_path = Path(plugin_dir)
        
        if not plugin_path.exists():
            logger.warning(f"Plugin directory not found: {plugin_dir}")
            return discovered
        
        for item in plugin_path.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                plugin_name = item.name
                
                try:
                    module = importlib.import_module(f"backend.plugins.{plugin_name}")
                    
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and issubclass(attr, Plugin) and attr != Plugin:
                            self.register_plugin_class(attr)
                            discovered.append(attr.metadata.name if hasattr(attr, 'metadata') else attr.__name__)
                            
                except ImportError as e:
                    logger.warning(f"Could not import plugin {plugin_name}: {e}")
        
        return discovered
    
    def load_plugin(self, name: str) -> Optional[Plugin]:
        """
        Load and instantiate a plugin.
        
        Args:
            name: Plugin name
            
        Returns:
            Plugin instance or None if not found
        """
        if name in self._plugins:
            return self._plugins[name]
        
        plugin_class = self._plugin_classes.get(name)
        
        if not plugin_class:
            logger.warning(f"Plugin class not found: {name}")
            return None
        
        try:
            plugin = plugin_class(self.app, self.db, self.api)
            self._plugins[name] = plugin
            logger.info(f"Loaded plugin: {name}")
            return plugin
        except Exception as e:
            logger.error(f"Error loading plugin {name}: {e}")
            return None
    
    def install_plugin(self, name: str, config: Dict = None) -> bool:
        """
        Install and enable a plugin.
        
        Args:
            name: Plugin name
            config: Optional configuration
            
        Returns:
            True if successful
        """
        plugin = self.load_plugin(name)
        
        if not plugin:
            return False
        
        try:
            plugin.install(self.app, self.db)
            
            if config:
                plugin.configure(config)
            
            plugin._enabled = True
            plugin._initialized = True
            
            if name not in self._enabled_plugins:
                self._enabled_plugins.append(name)
            
            self._subscribe_plugin_events(plugin)
            
            logger.info(f"Installed plugin: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Error installing plugin {name}: {e}")
            return False
    
    def uninstall_plugin(self, name: str) -> bool:
        """
        Uninstall a plugin.
        
        Args:
            name: Plugin name
            
        Returns:
            True if successful
        """
        plugin = self._plugins.get(name)
        
        if not plugin:
            return False
        
        try:
            plugin.uninstall()
            plugin._enabled = False
            
            if name in self._enabled_plugins:
                self._enabled_plugins.remove(name)
            
            logger.info(f"Uninstalled plugin: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Error uninstalling plugin {name}: {e}")
            return False
    
    def enable_plugin(self, name: str) -> bool:
        """
        Enable a plugin without reinstallation.
        
        Args:
            name: Plugin name
            
        Returns:
            True if successful
        """
        plugin = self._plugins.get(name)
        
        if not plugin:
            return self self.install_plugin(name)
        
        if not plugin.enabled:
            plugin._enabled = True
            if name not in self._enabled_plugins:
                self._enabled_plugins.append(name)
            self._subscribe_plugin_events(plugin)
        
        return True
    
    def disable_plugin(self, name: str) -> bool:
        """
        Disable a plugin without uninstallation.
        
        Args:
            name: Plugin name
            
        Returns:
            True if successful
        """
        plugin = self._plugins.get(name)
        
        if not plugin:
            return False
        
        plugin._enabled = False
        
        if name in self._enabled_plugins:
            self._enabled_plugins.remove(name)
        
        return True
    
    def get_plugin(self, name: str) -> Optional[Plugin]:
        """
        Get a plugin by name.
        
        Args:
            name: Plugin name
            
        Returns:
            Plugin instance or None
        """
        return self._plugins.get(name)
    
    def list_plugins(self, enabled_only: bool = False) -> List[Dict[str, Any]]:
        """
        List all plugins.
        
        Args:
            enabled_only: Only return enabled plugins
            
        Returns:
            List of plugin info dictionaries
        """
        result = []
        
        for name, plugin in self._plugins.items():
            if enabled_only and not plugin.enabled:
                continue
            
            result.append({
                "name": plugin.name,
                "version": plugin.version,
                "enabled": plugin.enabled,
                "initialized": plugin.initialized,
                "metadata": plugin.metadata.__dict__ if hasattr(plugin, 'metadata') else {},
            })
        
        return result
    
    def _subscribe_plugin_events(self, plugin: Plugin) -> None:
        """Subscribe plugin to event bus."""
        if not self._event_bus:
            return
        
        subscriptions = plugin.subscribe_to_events()
        
        for event_type, handler in subscriptions:
            self._event_bus.subscribe(event_type, handler)
            logger.debug(f"Plugin {plugin.name} subscribed to {event_type}")
    
    def reload_plugin(self, name: str) -> bool:
        """
        Reload a plugin (hot-reload).
        
        Args:
            name: Plugin name
            
        Returns:
            True if successful
        """
        if name in self._plugins:
            self.uninstall_plugin(name)
        
        return self.install_plugin(name)
    
    def get_all_routes(self) -> List[Dict[str, Any]]:
        """Collect routes from all enabled plugins."""
        routes = []
        
        for name in self._enabled_plugins:
            plugin = self._plugins.get(name)
            if plugin:
                routes.extend(plugin.get_routes())
        
        return routes
    
    def get_all_menu_items(self) -> List[Dict[str, Any]]:
        """Collect menu items from all enabled plugins."""
        items = []
        
        for name in self._enabled_plugins:
            plugin = self._plugins.get(name)
            if plugin:
                items.extend(plugin.get_menu_items())
        
        return items


_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """Get the global plugin manager instance."""
    global _manager
    if _manager is None:
        _manager = PluginManager()
    return _manager


def set_plugin_manager(manager: PluginManager) -> None:
    """Set the global plugin manager instance."""
    global _manager
    _manager = manager

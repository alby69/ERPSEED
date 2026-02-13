"""
Plugin Architecture Base Classes.

This module provides the base classes for implementing plugins in FlaskERP.
Plugins allow extending the system with new functionality without modifying the core.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class BasePlugin(ABC):
    """
    Base class for all plugins.
    
    Attributes:
        name: Unique identifier for the plugin.
        version: Plugin version string.
        description: Human-readable description.
        dependencies: List of other plugin names required by this plugin.
    """
    
    name: str = "base_plugin"
    version: str = "1.0.0"
    description: str = "Base plugin"
    dependencies: List[str] = []
    
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
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get plugin information.
        
        Returns:
            Dictionary with plugin metadata.
        """
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'dependencies': self.dependencies,
            'enabled': self.enabled
        }
    
    def before_request(self):
        """
        Hook called before each request.
        Override to add custom request processing.
        """
        pass
    
    def after_request(self, response):
        """
        Hook called after each request.
        
        Args:
            response: Flask response object.
            
        Returns:
            Modified response object.
        """
        return response


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

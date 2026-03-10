"""
Plugin System Package - Standardized plugin architecture for FlaskERP.

This package provides a modern plugin system with:
- Standard Plugin interface
- Plugin Manager for lifecycle management
- Event-driven communication
- Hot-reload support
"""

from .interfaces import Plugin, PluginMetadata
from .manager import PluginManager, get_plugin_manager

__all__ = [
    "Plugin",
    "PluginMetadata",
    "PluginManager",
    "get_plugin_manager",
]

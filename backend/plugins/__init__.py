"""
FlaskERP Plugin/Module System.

Plugins extend the core functionality without modifying it.
"""

from .base import BasePlugin, PluginMixin
from .registry import ModuleRegistry, PluginRegistry, register_plugin

__all__ = [
    "BasePlugin",
    "PluginMixin",
    "ModuleRegistry",
    "PluginRegistry",  # Backward compatibility
    "register_plugin",
]

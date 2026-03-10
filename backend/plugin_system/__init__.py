"""
Plugin System Package.

Exports the core components for plugin management.
"""
from .interfaces import Plugin
from .manager import PluginManager

__all__ = ["Plugin", "PluginManager"]
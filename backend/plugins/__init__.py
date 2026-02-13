"""
FlaskERP Plugin System.

Plugins extend the core functionality without modifying it.
"""
from .base import BasePlugin, PluginMixin
from .registry import PluginRegistry, register_plugin

__all__ = [
    'BasePlugin',
    'PluginMixin', 
    'PluginRegistry',
    'register_plugin',
]

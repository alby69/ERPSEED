"""
HR Plugin Entry Point.
"""
from backend.plugins.base import BasePlugin
from backend.plugins.registry import register_plugin
from .routes import blp


class HRPlugin(BasePlugin):
    """Human Resources plugin."""
    
    name = "hr"
    version = "1.0.0"
    description = "Human Resources management with Employees, Departments, Attendance, and Leave"
    dependencies = []
    
    def register(self):
        """Register HR blueprints."""
        if self.api:
            self.api.register_blueprint(blp)
    
    def init_db(self):
        """Initialize HR tables."""
        pass


def get_plugin():
    """Get HR plugin instance."""
    return HRPlugin


register_plugin(HRPlugin)

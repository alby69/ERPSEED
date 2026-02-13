"""
Accounting Plugin Entry Point.
"""
from backend.plugins.base import BasePlugin
from backend.plugins.registry import register_plugin
from .routes import blp


class AccountingPlugin(BasePlugin):
    """Double-entry accounting plugin."""
    
    name = "accounting"
    version = "1.0.0"
    description = "Double-entry accounting with Chart of Accounts, Journal, and Invoices"
    dependencies = []
    
    def register(self):
        """Register accounting blueprints."""
        if self.api:
            self.api.register_blueprint(blp)
    
    def init_db(self):
        """Initialize accounting tables."""
        pass


def get_plugin():
    """Get accounting plugin instance."""
    return AccountingPlugin


register_plugin(AccountingPlugin)

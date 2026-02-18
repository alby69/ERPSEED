"""
Inventory Plugin.

Provides inventory management functionality:
- Inventory Locations
- Stock Levels
- Stock Movements
- Inventory Counts
"""
from backend.plugins.base import BasePlugin


class InventoryPlugin(BasePlugin):
    """Inventory Management Plugin."""
    
    name = "inventory"
    description = "Inventory and Warehouse Management"
    version = "1.0.0"
    
    def register(self):
        """Register the plugin's routes."""
        from .routes import blp
        if self.api:
            self.api.register_blueprint(blp)
    
    def init_db(self):
        """Initialize plugin database models (called automatically by SQLAlchemy)."""
        # Models are defined but not explicitly initialized here
        # SQLAlchemy handles model registration automatically
        pass


def get_plugin():
    """Get plugin instance."""
    return InventoryPlugin

"""
Inventory Plugin.

Provides inventory management functionality:
- Inventory Locations
- Stock Levels
- Stock Movements
- Inventory Counts
"""
from typing import List
from plugins.base import BasePlugin
from plugins.registry import register_plugin


class InventoryPlugin(BasePlugin):
    """Inventory Management Plugin."""

    name = "inventory"
    version = "1.0.0"
    description = "Gestione magazzino, stock, movimenti, inventari"
    icon = "warehouse"

    # Licensing
    is_free = True
    plan_required = "starter"

    dependencies = ["products"]

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

    def get_menu_items(self, tenant_id: int) -> List[dict]:
        """Voci menu magazzino."""
        return [
            {
                'id': 'inventory',
                'label': 'Magazzino',
                'icon': 'warehouse',
                'menu_position': 60,
                'children': [
                    {
                        'id': 'locations',
                        'label': 'Ubicazioni',
                        'path': '/inventory/locations',
                        'icon': 'map-pin'
                    },
                    {
                        'id': 'stock',
                        'label': 'Giacenze',
                        'path': '/inventory/stock',
                        'icon': 'package'
                    },
                    {
                        'id': 'movements',
                        'label': 'Movimenti',
                        'path': '/inventory/movements',
                        'icon': 'truck'
                    },
                    {
                        'id': 'counts',
                        'label': 'Inventari',
                        'path': '/inventory/counts',
                        'icon': 'clipboard'
                    }
                ]
            }
        ]

    def get_widgets(self, tenant_id: int) -> List[dict]:
        """) -> List[Widget dashboard."""
        return [
            {
                'id': 'inventory_summary',
                'type': 'table',
                'title': 'Giacenze Magazzino',
                'size': 'medium',
                'menu_position': 60,
                'config': {
                    'columns': ['product', 'location', 'quantity'],
                    'data_source': 'inventory_summary'
                }
            },
            {
                'id': 'low_stock',
                'type': 'alert',
                'title': 'Scorte Basse',
                'size': 'small',
                'menu_position': 61,
                'config': {
                    'threshold': 10,
                    'data_source': 'low_stock_items'
                }
            }
        ]


def get_plugin():
    """Get plugin instance."""
    return InventoryPlugin


register_plugin(InventoryPlugin)

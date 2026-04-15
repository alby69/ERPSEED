"""
Accounting Plugin Entry Point.
"""
from typing import List
from plugins.base import BasePlugin
from plugins.registry import register_plugin
from .routes import blp


class AccountingPlugin(BasePlugin):
    """Double-entry accounting plugin."""

    name = "accounting"
    version = "1.0.0"
    description = "Contabilità con partita doppia, piano dei conti, registri"
    icon = "calculator"

    # Licensing
    is_free = True
    plan_required = "starter"

    dependencies = []

    def register(self):
        """Register accounting blueprints."""
        if self.api:
            self.api.register_blueprint(blp)

    def init_db(self):
        """Initialize accounting tables."""
        pass

    def get_menu_items(self, tenant_id: int) -> List[dict]:
        """Voci menu contabilità."""
        return [
            {
                'id': 'accounting',
                'label': 'Contabilità',
                'icon': 'calculator',
                'menu_position': 50,
                'children': [
                    {
                        'id': 'chart_of_accounts',
                        'label': 'Piano dei Conti',
                        'path': '/coa',
                        'icon': 'list'
                    },
                    {
                        'id': 'journal',
                        'label': 'Giornale',
                        'path': '/journal',
                        'icon': 'book'
                    },
                    {
                        'id': 'invoices',
                        'label': 'Fatture',
                        'path': '/invoices',
                        'icon': 'file-text'
                    },
                    {
                        'id': 'trial_balance',
                        'label': 'Bilancio di Verifica',
                        'path': '/trial-balance',
                        'icon': 'bar-chart'
                    }
                ]
            }
        ]

    def get_widgets(self, tenant_id: int) -> List[dict]:
        """Widget dashboard."""
        return [
            {
                'id': 'accounting_summary',
                'type': 'chart',
                'title': 'Situazione Contabile',
                'size': 'large',
                'menu_position': 50,
                'config': {
                    'chart_type': 'line',
                    'data_source': 'accounting_summary'
                }
            }
        ]


def get_plugin():
    """Get accounting plugin instance."""
    return AccountingPlugin


register_plugin(AccountingPlugin)

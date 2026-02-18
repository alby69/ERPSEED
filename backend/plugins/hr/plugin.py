"""
HR Plugin Entry Point.
"""
from typing import List
from backend.plugins.base import BasePlugin, register_plugin
from .routes import blp


class HRPlugin(BasePlugin):
    """Human Resources plugin."""
    
    name = "hr"
    version = "1.0.0"
    description = "Gestione risorse umane: dipendenti, reparti, presenze"
    icon = "users"
    
    # Licensing
    is_free = True
    plan_required = "starter"
    
    dependencies = []
    
    def register(self):
        """Register HR blueprints."""
        if self.api:
            self.api.register_blueprint(blp)
    
    def init_db(self):
        """Initialize HR tables."""
        pass
    
    def get_menu_items(self, tenant_id: int) -> List[dict]:
        """Voci menu HR."""
        return [
            {
                'id': 'hr',
                'label': 'Risorse Umane',
                'icon': 'users',
                'menu_position': 70,
                'children': [
                    {
                        'id': 'employees',
                        'label': 'Dipendenti',
                        'path': '/hr/employees',
                        'icon': 'user'
                    },
                    {
                        'id': 'departments',
                        'label': 'Reparti',
                        'path': '/hr/departments',
                        'icon': 'layers'
                    },
                    {
                        'id': 'attendance',
                        'label': 'Presenze',
                        'path': '/hr/attendance',
                        'icon': 'clock'
                    },
                    {
                        'id': 'leave',
                        'label': 'Permessi',
                        'path': '/hr/leave',
                        'icon': 'calendar'
                    }
                ]
            }
        ]
    
    def get_widgets(self, tenant_id: int) -> List[dict]:
        """Widget dashboard."""
        return [
            {
                'id': 'hr_summary',
                'type': 'stat',
                'title': 'Totale Dipendenti',
                'size': 'small',
                'menu_position': 70,
                'config': {
                    'icon': 'users',
                    'data_source': 'hr_employee_count'
                }
            }
        ]


def get_plugin():
    """Get HR plugin instance."""
    return HRPlugin


register_plugin(HRPlugin)

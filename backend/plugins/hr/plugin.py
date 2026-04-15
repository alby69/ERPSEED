"""
HR Plugin Entry Point.
"""

from typing import List
from backend.plugins.base import BasePlugin
from backend.plugins.registry import register_plugin
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

    def __init__(self, app=None, db=None, api=None):
        super().__init__(app, db, api)
        self._event_handlers = []

    def register(self):
        """Register HR blueprints."""
        if self.api:
            self.api.register_blueprint(blp)

    def init_db(self):
        """Initialize HR tables."""
        pass

    def subscribe_to_events(self, event_bus) -> list:
        """Subscribe to domain events."""
        from backend.shared.events import DomainEvent

        def on_user_created(event: DomainEvent):
            """Handle user created event - auto-create employee profile."""
            if event.payload.get("userId"):
                self._on_employee_auto_create(event.payload)

        def on_record_created(event: DomainEvent):
            """Handle record created event."""
            pass

        self._event_handlers = [
            ("user.created", on_user_created),
            ("record.created", on_record_created),
        ]

        for event_type, handler in self._event_handlers:
            event_bus.subscribe(event_type, handler)

        return self._event_handlers

    def _on_employee_auto_create(self, data: dict):
        """Auto-create employee when user is created."""
        pass

    def on_event(self, event_type: str, event_data: dict):
        """Handle incoming events."""
        if event_type == "user.created":
            self._on_employee_auto_create(event_data)

    def get_menu_items(self, tenant_id: int) -> List[dict]:
        """Voci menu HR."""
        return [
            {
                "id": "hr",
                "label": "Risorse Umane",
                "icon": "users",
                "menu_position": 70,
                "children": [
                    {
                        "id": "employees",
                        "label": "Dipendenti",
                        "path": "/hr/employees",
                        "icon": "user",
                    },
                    {
                        "id": "departments",
                        "label": "Reparti",
                        "path": "/hr/departments",
                        "icon": "layers",
                    },
                    {
                        "id": "attendance",
                        "label": "Presenze",
                        "path": "/hr/attendance",
                        "icon": "clock",
                    },
                    {
                        "id": "leave",
                        "label": "Permessi",
                        "path": "/hr/leave",
                        "icon": "calendar",
                    },
                ],
            }
        ]

    def get_widgets(self, tenant_id: int) -> List[dict]:
        """Widget dashboard."""
        return [
            {
                "id": "hr_summary",
                "type": "stat",
                "title": "Totale Dipendenti",
                "size": "small",
                "menu_position": 70,
                "config": {"icon": "users", "data_source": "hr_employee_count"},
            }
        ]


def get_plugin():
    """Get HR plugin instance."""
    return HRPlugin


register_plugin(HRPlugin)

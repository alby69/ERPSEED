"""
Domain Events for Analytics.
"""
from dataclasses import dataclass
from typing import Dict, Any

from backend.shared.events.event import DomainEvent


@dataclass
class ChartCreatedEvent(DomainEvent):
    def __init__(self, chart_id: int, chart_data: Dict[str, Any], tenant_id: int):
        super().__init__("chart.created", {"chart_id": chart_id, "chart_name": chart_data.get("name"),
            "chart_type": chart_data.get("chart_type"), "tenant_id": tenant_id})


@dataclass
class ChartDeletedEvent(DomainEvent):
    def __init__(self, chart_id: int, chart_data: Dict[str, Any], tenant_id: int):
        super().__init__("chart.deleted", {"chart_id": chart_id, "chart_name": chart_data.get("name"), "tenant_id": tenant_id})


@dataclass
class DashboardCreatedEvent(DomainEvent):
    def __init__(self, dashboard_id: int, dashboard_data: Dict[str, Any], tenant_id: int):
        super().__init__("dashboard.created", {"dashboard_id": dashboard_id, "dashboard_name": dashboard_data.get("name"),
            "tenant_id": tenant_id})

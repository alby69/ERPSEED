from dataclasses import dataclass
from typing import Dict, Any, List

class AnalyticsService:
    def execute(self, cmd_dict):
        # Fallback for missing analytics service logic
        return {"success": True, "data": {"items": []}}

def get_analytics_service():
    return AnalyticsService()
from .application.handlers import AnalyticsCommandHandler
from .application.commands.analytics_commands import (
    CreateChartCommand, UpdateChartCommand, DeleteChartCommand,
    CreateDashboardCommand, UpdateDashboardCommand, DeleteDashboardCommand
)
from backend.models import SysChart, SysDashboard, ChartLibraryConfig
from backend.extensions import db
from backend.core.utils.utils import apply_filters, apply_sorting, paginate

class AnalyticsService:
    def __init__(self):
        self.handler = AnalyticsCommandHandler()

    def create_chart(self, data):
        cmd = CreateChartCommand(**data)
        return self.handler.handle_create_chart(cmd)

    def update_chart(self, chart_id, data):
        cmd = UpdateChartCommand(chart_id, data)
        return self.handler.handle_update_chart(cmd)

    def delete_chart(self, chart_id):
        cmd = DeleteChartCommand(chart_id)
        return self.handler.handle_delete_chart(cmd)

    def list_charts(self):
        return SysChart.query.all()

    def get_chart(self, chart_id):
        return db.session.get(SysChart, chart_id)

    def create_dashboard(self, data):
        cmd = CreateDashboardCommand(**data)
        return self.handler.handle_create_dashboard(cmd)

    def update_dashboard(self, dashboard_id, data):
        cmd = UpdateDashboardCommand(dashboard_id, data)
        return self.handler.handle_update_dashboard(cmd)

    def delete_dashboard(self, dashboard_id):
        cmd = DeleteDashboardCommand(dashboard_id)
        return self.handler.handle_delete_dashboard(cmd)

    def list_dashboards(self):
        return SysDashboard.query.all()

    def get_dashboard(self, dashboard_id):
        return db.session.get(SysDashboard, dashboard_id)

    def execute(self, cmd_dict):
        # Compatibility method
        command = cmd_dict.get("command")
        if command == "ListChartLibraries":
            items = ChartLibraryConfig.query.all()
            return {"success": True, "data": {"items": items}}
        if command == "ListCharts":
            items = SysChart.query.all()
            return {"success": True, "data": {"items": items}}
        return {"success": True, "data": {"items": []}}

_analytics_service = None

def get_analytics_service():
    global _analytics_service
    if _analytics_service is None:
        _analytics_service = AnalyticsService()
    return _analytics_service

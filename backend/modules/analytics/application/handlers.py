from backend.models import SysChart, SysDashboard
from backend.extensions import db
from flask_smorest import abort

class AnalyticsCommandHandler:
    def handle_create_chart(self, cmd):
        chart = SysChart(
            title=cmd.title,
            library=cmd.library,
            chart_type=cmd.chart_type,
            modelId=cmd.modelId,
            x_axis=cmd.x_axis,
            y_axis=cmd.y_axis,
            aggregation=cmd.aggregation,
            filters=cmd.filters,
            filters_config=cmd.filters_config,
            library_options=cmd.library_options
        )
        db.session.add(chart)
        db.session.commit()
        return chart

    def handle_update_chart(self, cmd):
        chart = db.session.get(SysChart, cmd.chart_id)
        if not chart:
            abort(404, message="Chart not found.")
        for key, value in cmd.data.items():
            if hasattr(chart, key):
                setattr(chart, key, value)
        db.session.commit()
        return chart

    def handle_delete_chart(self, cmd):
        chart = db.session.get(SysChart, cmd.chart_id)
        if not chart:
            abort(404, message="Chart not found.")
        db.session.delete(chart)
        db.session.commit()
        return True

    def handle_create_dashboard(self, cmd):
        dashboard = SysDashboard(
            title=cmd.title,
            description=cmd.description,
            layout=cmd.layout,
            is_public=cmd.is_public,
            refresh_interval=cmd.refresh_interval,
            default_library=cmd.default_library,
            created_by=cmd.created_by
        )
        db.session.add(dashboard)
        db.session.commit()
        return dashboard

    def handle_update_dashboard(self, cmd):
        dashboard = db.session.get(SysDashboard, cmd.dashboard_id)
        if not dashboard:
            abort(404, message="Dashboard not found.")
        for key, value in cmd.data.items():
            if hasattr(dashboard, key):
                setattr(dashboard, key, value)
        db.session.commit()
        return dashboard

    def handle_delete_dashboard(self, cmd):
        dashboard = db.session.get(SysDashboard, cmd.dashboard_id)
        if not dashboard:
            abort(404, message="Dashboard not found.")
        db.session.delete(dashboard)
        db.session.commit()
        return True

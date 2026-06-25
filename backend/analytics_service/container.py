"""
Container - Dependency Injection for Analytics Service.
"""
from backend.container import get_container as get_global_container
from backend.analytics_service.infrastructure.repository import ChartRepository, ChartLibraryRepository
from backend.analytics_service.api import AnalyticsService


def register_analytics_service(container=None):
    if container is None: container = get_global_container()
    container.register('chart_repository', lambda: ChartRepository(), singleton=True)
    container.register('chart_library_repository', lambda: ChartLibraryRepository(), singleton=True)
    container.register('analytics_service', lambda: AnalyticsService(
        chart_repository=container.get('chart_repository'),
        library_repository=container.get('chart_library_repository'),
        event_bus=container.get('event_bus') if container._providers.get('event_bus') else None
    ), singleton=True)
    return container


def get_analytics_service():
    container = get_global_container()
    return container.get('analytics_service')

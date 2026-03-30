"""
Container - Dependency Injection for Sales Service.
"""
from backend.core.container import get_container as get_global_container
from backend.core.container import get_container as get_global_container
from backend.modules.sales.infrastructure.repository import SalesOrderRepository
from backend.modules.sales.service_api import SalesService


def register_sales_service(container=None):
    if container is None:
        container = get_global_container()
    
    container.register('sales_repository', lambda: SalesOrderRepository(), singleton=True)
    container.register('sales_service', lambda: SalesService(
        repository=container.get('sales_repository'),
        event_bus=container.get('event_bus') if container._providers.get('event_bus') else None
    ), singleton=True)
    
    return container


def get_sales_service():
    container = get_global_container()
    return container.get('sales_service')


def get_sales_repository():
    container = get_global_container()
    return container.get('sales_repository')

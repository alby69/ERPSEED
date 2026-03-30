"""
Container - Dependency Injection for Purchases Service.
"""
from backend.core.container import get_container as get_global_container
from backend.core.container import get_container as get_global_container
from backend.modules.purchases.infrastructure.repository import PurchaseOrderRepository
from backend.modules.purchases.service_api import PurchaseService


def register_purchases_service(container=None):
    if container is None: container = get_global_container()
    container.register('purchases_repository', lambda: PurchaseOrderRepository(), singleton=True)
    container.register('purchases_service', lambda: PurchaseService(
        repository=container.get('purchases_repository'),
        event_bus=container.get('event_bus') if container._providers.get('event_bus') else None
    ), singleton=True)
    return container


def get_purchases_service():
    container = get_global_container()
    return container.get('purchases_service')


def get_purchases_repository():
    container = get_global_container()
    return container.get('purchases_repository')

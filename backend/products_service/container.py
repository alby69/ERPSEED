"""
Container - Dependency Injection for Products Service.
"""
from backend.container import get_container as get_global_container
from backend.products_service.infrastructure.repository import ProductRepository
from backend.products_service.api import ProductService


def register_products_service(container=None):
    """Register products service in the DI container."""
    if container is None:
        container = get_global_container()
    
    container.register('products_repository', lambda: ProductRepository(), singleton=True)
    container.register('products_service', lambda: ProductService(
        repository=container.get('products_repository'),
        event_bus=container.get('event_bus') if container._providers.get('event_bus') else None
    ), singleton=True)
    
    return container


def get_products_service():
    """Get the products service from the container."""
    container = get_global_container()
    return container.get('products_service')


def get_products_repository():
    """Get the products repository from the container."""
    container = get_global_container()
    return container.get('products_repository')

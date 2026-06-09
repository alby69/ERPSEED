from backend.core.container import get_container as get_global_container
from backend.modules.tax.infrastructure.repository import TaxRateRepository
from backend.modules.tax.service_api import TaxService


def register_tax_service(container=None):
    if container is None:
        container = get_global_container()

    container.register('tax_repository', lambda: TaxRateRepository(), singleton=True)
    container.register('tax_service', lambda: TaxService(
        repository=container.get('tax_repository'),
        event_bus=container.get('event_bus') if container._providers.get('event_bus') else None
    ), singleton=True)

    return container


def get_tax_service():
    container = get_global_container()
    return container.get('tax_service')


def get_tax_repository():
    container = get_global_container()
    return container.get('tax_repository')

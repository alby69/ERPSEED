from backend.core.container import get_container as get_global_container
from .infrastructure.repository import InvoiceRepository
from .service_api import InvoicingService


def register_invoicing_service(container=None):
    if container is None:
        container = get_global_container()
    container.register("invoice_repository", lambda: InvoiceRepository(), singleton=True)
    container.register("invoicing_service", lambda: InvoicingService(
        repository=container.get("invoice_repository"),
    ), singleton=True)
    return container


def get_invoicing_service():
    container = get_global_container()
    return container.get("invoicing_service")

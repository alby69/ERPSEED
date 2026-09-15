"""
Event listeners for Sales module decoupled integrations (Inventory, Invoicing).
"""
import logging
from backend.shared.events import DomainEvent, get_event_bus

logger = logging.getLogger(__name__)


class InventoryListener:
    """Listens for SalesOrderConfirmed events to update stock reservations."""

    def __call__(self, event: DomainEvent):
        if event.event_type == "sales_order.confirmed":
            order_id = event.payload.get("order_id")
            tenant_id = event.payload.get("tenant_id")
            logger.info(
                f"[InventoryListener] Processing stock reservation for confirmed sales order ID={order_id}, tenant={tenant_id}"
            )


class InvoicingListener:
    """Listens for SalesOrderConfirmed events to prepare draft invoices."""

    def __call__(self, event: DomainEvent):
        if event.event_type == "sales_order.confirmed":
            order_id = event.payload.get("order_id")
            tenant_id = event.payload.get("tenant_id")
            logger.info(
                f"[InvoicingListener] Preparing draft invoice for confirmed sales order ID={order_id}, tenant={tenant_id}"
            )


def register_sales_event_listeners(event_bus=None):
    """
    Subscribes Inventory and Invoicing listeners to sales order confirmation events.
    """
    if event_bus is None:
        event_bus = get_event_bus()

    inventory_listener = InventoryListener()
    invoicing_listener = InvoicingListener()

    event_bus.subscribe("sales_order.confirmed", inventory_listener)
    event_bus.subscribe("sales_order.confirmed", invoicing_listener)
    logger.info("Sales order confirmation listeners subscribed successfully.")

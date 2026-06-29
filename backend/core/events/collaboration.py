"""
Multi-Agent Collaboration Handlers.
Implements cross-agent workflows using the EventBus.
"""

import logging
from backend.shared.events.event_bus import EventBus
from backend.modules.sales.domain import SalesOrderCreatedEvent
from backend.modules.purchases.application.commands import CreatePurchaseOrderCommand
# Correcting imports based on actual module structure
from backend.modules.purchases.service_api import get_purchase_service

logger = logging.getLogger(__name__)

class AutoReplenishmentAgent:
    """
    Collaboration Agent that monitors sales and triggers purchase requests
    if stock is low or for specific business rules.
    """

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self._subscribe()

    def _subscribe(self):
        self.event_bus.subscribe("SalesOrderCreated", self.handle_sales_order)
        logger.info("AutoReplenishmentAgent subscribed to SalesOrderCreated")

    def handle_sales_order(self, event: SalesOrderCreatedEvent):
        """
        When a sales order is created, check if we need to order more from suppliers.
        This is a collaboration between SalesAgent and PurchaseAgent.
        """
        logger.info(f"Collaboration: Analyzing sales order {event.order_id} for replenishment")

        # In a real scenario, we would check stock levels here.
        # Simulating a rule: if order has more than 5 items of a product, auto-purchase.

        order_data = event.order_data
        lines = order_data.get("lines", [])

        for line in lines:
            if line.get("quantity", 0) > 5:
                self._trigger_purchase_order(line, event.tenant_id)

    def _trigger_purchase_order(self, sales_line: dict, tenant_id: int):
        """Delegates the purchase task to the PurchaseAgent."""
        logger.info(f"Collaboration: Triggering PurchaseAgent for product {sales_line.get('product_id')}")

        purchase_service = get_purchase_service()

        # Create a purchase order command
        cmd = CreatePurchaseOrderCommand(
            tenant_id=tenant_id,
            number=f"AUTO-PURCH-{sales_line.get('product_id')}",
            date="2025-01-01", # Should be current date
            supplier_id=1, # Default or looked up supplier
            notes=f"Auto-replenishment from sales order line",
            lines=[{
                "product_id": sales_line.get("product_id"),
                "quantity": sales_line.get("quantity") * 2, # Reorder double
                "price": 0.0 # To be negotiated
            }]
        )

        try:
            # We bypass the API and call the service/handler directly for agent-to-agent talk
            purchase_service.create_order(cmd)
            logger.info("Collaboration: PurchaseAgent successfully created replenishment order")
        except Exception as e:
            logger.error(f"Collaboration: PurchaseAgent failed to create order: {e}")

def register_collaboration_agents(event_bus: EventBus):
    AutoReplenishmentAgent(event_bus)

"""
Domain Events for Sales Service.
"""
from dataclasses import dataclass
from typing import Any, Dict

from shared.events.event import DomainEvent


@dataclass
class SalesOrderCreatedEvent(DomainEvent):
    def __init__(self, orderId: int, order_data: Dict[str, Any], tenant_id: int):
        super().__init__(
            event_type="sales_order.created",
            payload={
                "orderId": orderId,
                "order_number": order_data.get("number"),
                "customer_id": order_data.get("customer_id"),
                "total_amount": order_data.get("total_amount"),
                "tenant_id": tenant_id,
            }
        )


@dataclass
class SalesOrderUpdatedEvent(DomainEvent):
    def __init__(self, orderId: int, old_data: Dict, new_data: Dict, tenant_id: int):
        super().__init__(
            event_type="sales_order.updated",
            payload={
                "orderId": orderId,
                "old_status": old_data.get("status"),
                "new_status": new_data.get("status"),
                "tenant_id": tenant_id,
            }
        )


@dataclass
class SalesOrderConfirmedEvent(DomainEvent):
    def __init__(self, orderId: int, order_data: Dict, tenant_id: int):
        super().__init__(
            event_type="sales_order.confirmed",
            payload={
                "orderId": orderId,
                "order_number": order_data.get("number"),
                "total_amount": order_data.get("total_amount"),
                "tenant_id": tenant_id,
            }
        )


@dataclass
class SalesOrderCancelledEvent(DomainEvent):
    def __init__(self, orderId: int, order_data: Dict, tenant_id: int):
        super().__init__(
            event_type="sales_order.cancelled",
            payload={
                "orderId": orderId,
                "order_number": order_data.get("number"),
                "tenant_id": tenant_id,
            }
        )


@dataclass
class SalesOrderDeletedEvent(DomainEvent):
    def __init__(self, orderId: int, order_data: Dict, tenant_id: int):
        super().__init__(
            event_type="sales_order.deleted",
            payload={
                "orderId": orderId,
                "order_number": order_data.get("number"),
                "tenant_id": tenant_id,
            }
        )

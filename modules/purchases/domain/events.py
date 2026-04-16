"""
Domain Events for Purchases Service.
"""
from dataclasses import dataclass
from typing import Dict, Any

from shared.events.event import DomainEvent


@dataclass
class PurchaseOrderCreatedEvent(DomainEvent):
    def __init__(self, order_id: int, order_data: Dict[str, Any], tenant_id: int):
        super().__init__("purchase_order.created", {"order_id": order_id, "order_number": order_data.get("number"),
            "supplier_id": order_data.get("supplier_id"), "total_amount": order_data.get("total_amount"), "tenant_id": tenant_id})


@dataclass
class PurchaseOrderUpdatedEvent(DomainEvent):
    def __init__(self, order_id: int, old_data: Dict, new_data: Dict, tenant_id: int):
        super().__init__("purchase_order.updated", {"order_id": order_id, "old_status": old_data.get("status"),
            "new_status": new_data.get("status"), "tenant_id": tenant_id})


@dataclass
class PurchaseOrderConfirmedEvent(DomainEvent):
    def __init__(self, order_id: int, order_data: Dict, tenant_id: int):
        super().__init__("purchase_order.confirmed", {"order_id": order_id, "order_number": order_data.get("number"),
            "total_amount": order_data.get("total_amount"), "tenant_id": tenant_id})


@dataclass
class PurchaseOrderReceivedEvent(DomainEvent):
    def __init__(self, order_id: int, order_data: Dict, tenant_id: int):
        super().__init__("purchase_order.received", {"order_id": order_id, "order_number": order_data.get("number"),
            "total_amount": order_data.get("total_amount"), "tenant_id": tenant_id})


@dataclass
class PurchaseOrderCancelledEvent(DomainEvent):
    def __init__(self, order_id: int, order_data: Dict, tenant_id: int):
        super().__init__("purchase_order.cancelled", {"order_id": order_id, "order_number": order_data.get("number"),
            "tenant_id": tenant_id})

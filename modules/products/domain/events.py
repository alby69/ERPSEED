"""
Domain Events for Products Service.

Events are published when significant domain actions occur.
Other services can subscribe to these events to react accordingly.
"""
from dataclasses import dataclass
from typing import Any, Dict

from shared.events.event import DomainEvent


@dataclass
class ProductCreatedEvent(DomainEvent):
    """Published when a new product is created."""

    def __init__(self, product_id: int, product_data: Dict[str, Any], tenant_id: int):
        super().__init__(
            event_type="product.created",
            payload={
                "product_id": product_id,
                "product_name": product_data.get("name"),
                "product_code": product_data.get("code"),
                "tenant_id": tenant_id,
            }
        )


@dataclass
class ProductUpdatedEvent(DomainEvent):
    """Published when a product is updated."""

    def __init__(self, product_id: int, old_data: Dict[str, Any], new_data: Dict[str, Any], tenant_id: int):
        super().__init__(
            event_type="product.updated",
            payload={
                "product_id": product_id,
                "old_data": old_data,
                "new_data": new_data,
                "tenant_id": tenant_id,
            }
        )


@dataclass
class ProductDeletedEvent(DomainEvent):
    """Published when a product is deleted."""

    def __init__(self, product_id: int, product_data: Dict[str, Any], tenant_id: int):
        super().__init__(
            event_type="product.deleted",
            payload={
                "product_id": product_id,
                "product_name": product_data.get("name"),
                "product_code": product_data.get("code"),
                "tenant_id": tenant_id,
            }
        )


@dataclass
class ProductStockChangedEvent(DomainEvent):
    """Published when product stock changes."""

    def __init__(self, product_id: int, old_stock: float, new_stock: float, reason: str, tenant_id: int):
        super().__init__(
            event_type="product.stock_changed",
            payload={
                "product_id": product_id,
                "old_stock": old_stock,
                "new_stock": new_stock,
                "change": new_stock - old_stock,
                "reason": reason,
                "tenant_id": tenant_id,
            }
        )


@dataclass
class ProductLowStockEvent(DomainEvent):
    """Published when product stock falls below reorder level."""

    def __init__(self, product_id: int, current_stock: float, reorder_level: float, tenant_id: int):
        super().__init__(
            event_type="product.low_stock",
            payload={
                "product_id": product_id,
                "current_stock": current_stock,
                "reorder_level": reorder_level,
                "tenant_id": tenant_id,
            }
        )

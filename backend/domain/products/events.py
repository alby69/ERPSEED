"""
Domain Events for Products.

Events published when significant domain actions occur.
"""
from dataclasses import dataclass
from typing import Any, Dict

from backend.shared.events.event import DomainEvent


@dataclass
class ProductCreatedEvent(DomainEvent):
    def __init__(self, product_id: int, product_data: Dict[str, Any], tenant_id: int):
        super().__init__("product.created", {"product_id": product_id, "product_name": product_data.get("name"),
            "product_code": product_data.get("code"), "tenant_id": tenant_id})


@dataclass
class ProductUpdatedEvent(DomainEvent):
    def __init__(self, product_id: int, old_data: Dict[str, Any], new_data: Dict[str, Any], tenant_id: int):
        super().__init__("product.updated", {"product_id": product_id, "old_data": old_data, "new_data": new_data,
            "tenant_id": tenant_id})


@dataclass
class ProductDeletedEvent(DomainEvent):
    def __init__(self, product_id: int, product_data: Dict[str, Any], tenant_id: int):
        super().__init__("product.deleted", {"product_id": product_id, "product_name": product_data.get("name"),
            "product_code": product_data.get("code"), "tenant_id": tenant_id})


@dataclass
class ProductStockChangedEvent(DomainEvent):
    def __init__(self, product_id: int, old_stock: float, new_stock: float, reason: str, tenant_id: int):
        super().__init__("product.stock_changed", {"product_id": product_id, "old_stock": old_stock,
            "new_stock": new_stock, "change": new_stock - old_stock, "reason": reason, "tenant_id": tenant_id})


@dataclass
class ProductLowStockEvent(DomainEvent):
    def __init__(self, product_id: int, current_stock: float, reorder_level: float, tenant_id: int):
        super().__init__("product.low_stock", {"product_id": product_id, "current_stock": current_stock,
            "reorder_level": reorder_level, "tenant_id": tenant_id})

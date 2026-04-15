"""
Purchases Service Package - Modular purchase order management service.

Usage:
    from modules.purchases import execute

    # Create an order
    result = execute({
        "command": "CreatePurchaseOrder",
        "tenant_id": 1,
        "number": "PO-001",
        "supplier_id": 1,
        "lines": [{"product_id": 1, "quantity": 10, "unit_price": 25.00}]
    })

    # List orders
    result = execute({
        "command": "ListPurchaseOrders",
        "tenant_id": 1
    })

Architecture:
    ├── api.py              # Main entry point (execute function)
    ├── container.py        # Dependency injection
    ├── domain/            # Domain models and events
    ├── application/       # Commands and handlers
    └── infrastructure/    # Repository implementations
"""

from .service_api import PurchaseService, execute, get_purchase_service
from .container import register_purchases_service, get_purchases_service

__version__ = "1.0.0"

__all__ = ["PurchaseService", "execute", "get_purchase_service", "register_purchases_service", "get_purchase_service"]

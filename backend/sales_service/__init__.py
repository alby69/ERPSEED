"""
Sales Service Package - Modular sales order management service.

Usage:
    from backend.sales_service import execute
    
    # Create an order
    result = execute({
        "command": "CreateSalesOrder",
        "tenant_id": 1,
        "number": "ORD-001",
        "customer_id": 1,
        "lines": [
            {"product_id": 1, "quantity": 2, "unit_price": 50.00}
        ]
    })
    
    # List orders
    result = execute({
        "command": "ListSalesOrders",
        "tenant_id": 1
    })

Architecture:
    ├── api.py              # Main entry point (execute function)
    ├── container.py        # Dependency injection
    ├── domain/             # Domain models and events
    │   ├── models.py       # SalesOrder, SalesOrderLine
    │   └── events.py       # Domain events
    ├── application/        # Commands and handlers
    │   ├── commands/       # Command classes
    │   └── handlers.py     # Handler implementations
    └── infrastructure/     # External dependencies
        └── repository.py    # SQLAlchemy repository
"""

from .api import SalesService, execute, get_sales_service
from .container import register_sales_service, get_sales_service

__version__ = "1.0.0"

__all__ = [
    "SalesService",
    "execute",
    "get_sales_service",
    "register_sales_service",
    "get_sales_service",
]

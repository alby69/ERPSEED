"""
Products Service Package - Modular product management service.

This service follows the Command Handler pattern and provides a JSON-based API
for all product operations. It is fully testable and can be used from CLI,
frontend, or other services.

Usage:
    from backend.modules.products import execute

    # Create a product
    result = execute({
        "command": "CreateProduct",
        "tenant_id": 1,
        "name": "My Product",
        "code": "PROD-001",
        "unit_price": 100.00
    })

    # List products
    result = execute({
        "command": "ListProducts",
        "tenant_id": 1
    })

Architecture:
    ├── api.py              # Main entry point (execute function)
    ├── container.py        # Dependency injection
    ├── domain/             # Domain models and events
    │   ├── models.py       # Product, ProductList
    │   └── events.py       # Domain events
    ├── application/        # Commands and handlers
    │   ├── commands/       # Command classes
    │   ├── queries/        # Query classes
    │   └── handlers.py     # Handler implementations
    └── infrastructure/     # External dependencies
        └── repository.py   # SQLAlchemy repository
"""

from .service_api import ProductService, execute, get_product_service
from .container import register_products_service, get_products_service

__version__ = "1.0.0"

__all__ = [
    "ProductService",
    "execute",
    "get_product_service",
    "register_products_service",
    "get_products_service",
]

"""
Marketplace Module - DEPRECATED.

DEPRECATED: Use the new CQRS structure:
- backend.endpoints.marketplace for REST API
- backend.domain.marketplace for domain models
- backend.application.marketplace for commands and handlers
- backend.infrastructure.marketplace for repositories

This module is kept for backward compatibility with existing imports.
"""
import warnings
warnings.warn(
    "backend.marketplace is deprecated. Use backend.endpoints.marketplace instead.",
    DeprecationWarning,
    stacklevel=2
)

from .models import (
    Category,
    BlockListing,
    Review,
    PaymentTransaction,
    Author,
    create_default_categories,
)

__all__ = [
    "Category",
    "BlockListing",
    "Review",
    "PaymentTransaction",
    "Author",
    "create_default_categories",
]

"""
Exceptions Package - Custom exceptions for FlaskERP.
"""

from .flaskerp_exceptions import (
    FlaskERPException,
    NotFoundError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    ServiceUnavailableError,
)

__all__ = [
    "FlaskERPException",
    "NotFoundError",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "ConflictError",
    "ServiceUnavailableError",
]

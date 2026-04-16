"""
Exceptions Package - Custom exceptions for FlaskERP.
"""

from typing import Optional, Any


class FlaskERPException(Exception):
    """Base exception for FlaskERP."""

    def __init__(self, message: str, code: str = "ERROR", details: Any = None):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(self.message)


class NotFoundError(FlaskERPException):
    """Resource not found."""

    def __init__(self, resource: str, resource_id: Any = None):
        msg = f"{resource} not found"
        if resource_id:
            msg += f" (id: {resource_id})"
        super().__init__(msg, code="NOT_FOUND")


class ValidationError(FlaskERPException):
    """Validation error."""

    def __init__(self, message: str, field: str = None):
        super().__init__(message, code="VALIDATION_ERROR", details={"field": field})


class AuthenticationError(FlaskERPException):
    """Authentication failed."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, code="AUTH_ERROR")


class AuthorizationError(FlaskERPException):
    """Authorization failed."""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, code="FORBIDDEN")


class ConflictError(FlaskERPException):
    """Resource conflict."""

    def __init__(self, message: str, resource: str = None):
        super().__init__(message, code="CONFLICT", details={"resource": resource})


class ServiceUnavailableError(FlaskERPException):
    """Service temporarily unavailable."""

    def __init__(self, message: str = "Service unavailable"):
        super().__init__(message, code="SERVICE_UNAVAILABLE")

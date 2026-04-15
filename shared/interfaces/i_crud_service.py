"""
Interfaces Package - Abstract interfaces for service contracts.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any


class ITenantService(ABC):
    """Interface for tenant management."""

    @abstractmethod
    def get_current_tenant(self) -> Optional[str]:
        """Get current tenant identifier."""
        pass

    @abstractmethod
    def set_tenant(self, tenant_id: str) -> None:
        """Set current tenant context."""
        pass

    @abstractmethod
    def list_tenants(self, userId: int) -> List[Dict[str, Any]]:
        """List all tenants accessible by user."""
        pass

    @abstractmethod
    def create_tenant(self, name: str, owner_id: int) -> Dict[str, Any]:
        """Create a new tenant."""
        pass


class IAuthService(ABC):
    """Interface for authentication."""

    @abstractmethod
    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and return token."""
        pass

    @abstractmethod
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload."""
        pass

    @abstractmethod
    def refresh_token(self, refresh_token: str) -> Optional[str]:
        """Refresh access token."""
        pass

    @abstractmethod
    def logout(self, token: str) -> bool:
        """Invalidate token."""
        pass


class ICrudService(ABC):
    """Interface for CRUD operations on entities."""

    @abstractmethod
    def create(self, model_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record."""
        pass

    @abstractmethod
    def read(self, model_name: str, record_id: int) -> Optional[Dict[str, Any]]:
        """Read a single record."""
        pass

    @abstractmethod
    def update(
        self, model_name: str, record_id: int, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update a record."""
        pass

    @abstractmethod
    def delete(self, model_name: str, record_id: int) -> bool:
        """Delete a record (soft delete)."""
        pass

    @abstractmethod
    def list(
        self, model_name: str, domain: List = None, **kwargs
    ) -> List[Dict[str, Any]]:
        """List records with filtering."""
        pass

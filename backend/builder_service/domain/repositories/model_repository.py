"""
Model Repository Interface - Repository pattern for model persistence.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class ModelRepository(ABC):
    """
    Abstract repository for model definitions.
    Implements the Repository pattern to separate domain from data access.
    """

    @abstractmethod
    def find_by_id(self, model_id: int) -> Optional[Dict[str, Any]]:
        """Find a model by ID."""
        pass

    @abstractmethod
    def find_by_technical_name(
        self, technical_name: str, project_id: int
    ) -> Optional[Dict[str, Any]]:
        """Find a model by technical name within a project."""
        pass

    @abstractmethod
    def find_by_project(self, project_id: int) -> List[Dict[str, Any]]:
        """Find all models in a project."""
        pass

    @abstractmethod
    def save(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update a model."""
        pass

    @abstractmethod
    def delete(self, model_id: int) -> bool:
        """Delete a model."""
        pass

    @abstractmethod
    def add_field(self, model_id: int, field_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a field to a model."""
        pass

    @abstractmethod
    def update_field(self, field_id: int, field_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a field."""
        pass

    @abstractmethod
    def delete_field(self, field_id: int) -> bool:
        """Delete a field."""
        pass

    @abstractmethod
    def get_fields(self, model_id: int) -> List[Dict[str, Any]]:
        """Get all fields for a model."""
        pass


class FieldRepository(ABC):
    """Abstract repository for field definitions."""

    @abstractmethod
    def find_by_id(self, field_id: int) -> Optional[Dict[str, Any]]:
        """Find a field by ID."""
        pass

    @abstractmethod
    def find_by_model(self, model_id: int) -> List[Dict[str, Any]]:
        """Find all fields for a model."""
        pass

    @abstractmethod
    def save(self, field_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update a field."""
        pass

    @abstractmethod
    def delete(self, field_id: int) -> bool:
        """Delete a field."""
        pass

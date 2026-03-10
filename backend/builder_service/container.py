"""
Builder Service Container - Dependency injection for Builder services.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class BuilderServiceContainer:
    """Container for Builder service dependencies."""

    def __init__(self):
        self._repository = None
        self._model_service = None
        self._event_bus = None

    def set_event_bus(self, event_bus) -> None:
        """Set the event bus."""
        self._event_bus = event_bus

    def get_repository(self, db=None):
        """Get or create the model repository."""
        if self._repository is None:
            from .infrastructure.persistence.sqlalchemy_repository import (
                SQLAlchemyModelRepository,
            )

            self._repository = SQLAlchemyModelRepository(db)
        return self._repository

    def get_model_service(self, db=None) -> "ModelService":
        """Get or create the model service."""
        if self._model_service is None:
            from .services.model_service import ModelService

            repository = self.get_repository(db)
            self._model_service = ModelService(
                repository=repository,
                event_bus=self._event_bus,
            )
        return self._model_service


_container: Optional[BuilderServiceContainer] = None


def get_builder_container() -> BuilderServiceContainer:
    """Get the global Builder service container."""
    global _container
    if _container is None:
        _container = BuilderServiceContainer()
    return _container


def get_model_service(db=None):
    """Convenience function to get the model service."""
    return get_builder_container().get_model_service(db)

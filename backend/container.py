"""
Service Container - Dependency Injection container for ERPSeed services.
"""

from typing import Any, Callable, Dict, Optional
import logging
from threading import Lock

logger = logging.getLogger(__name__)


class ServiceContainer:
    """Dependency injection container for managing service instances."""

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._lock = Lock()
        logger.info("ServiceContainer initialized")

    def register(self, name: str, factory: Callable, singleton: bool = True) -> None:
        """Register a service with a factory function.

        Args:
            name: Service name identifier
            factory: Factory function that creates the service instance
            singleton: If True, only one instance is created (default)
        """
        with self._lock:
            self._factories[name] = (factory, singleton)
            if name in self._services:
                del self._services[name]
            logger.debug(f"Service registered: {name} (singleton={singleton})")

    def register_instance(self, name: str, instance: Any) -> None:
        """Register an existing instance as a service.

        Args:
            name: Service name identifier
            instance: The service instance
        """
        with self._lock:
            self._services[name] = instance
            if name in self._factories:
                del self._factories[name]
            logger.debug(f"Instance registered: {name}")

    def get(self, name: str) -> Optional[Any]:
        """Get a service by name.

        Args:
            name: Service name identifier

        Returns:
            Service instance or None if not found
        """
        with self._lock:
            if name in self._services:
                return self._services[name]

            if name in self._factories:
                factory, singleton = self._factories[name]
                instance = factory()

                if singleton:
                    self._services[name] = instance
                    logger.debug(f"Service created and cached: {name}")
                else:
                    logger.debug(f"Service created (non-singleton): {name}")

                return instance

            logger.warning(f"Service not found: {name}")
            return None

    def has(self, name: str) -> bool:
        """Check if a service is registered.

        Args:
            name: Service name identifier

        Returns:
            True if service is registered
        """
        return name in self._services or name in self._factories

    def clear(self) -> None:
        """Clear all registered services."""
        with self._lock:
            self._services.clear()
            self._factories.clear()
            logger.info("ServiceContainer cleared")

    def unregister(self, name: str) -> None:
        """Unregister a service.

        Args:
            name: Service name identifier
        """
        with self._lock:
            if name in self._services:
                del self._services[name]
            if name in self._factories:
                del self._factories[name]
            logger.debug(f"Service unregistered: {name}")


_container: Optional[ServiceContainer] = None
_container_lock = Lock()


def get_container() -> ServiceContainer:
    """Get the global ServiceContainer instance."""
    global _container
    if _container is None:
        with _container_lock:
            if _container is None:
                _container = ServiceContainer()
    return _container


def set_container(container: ServiceContainer) -> None:
    """Set the global container instance."""
    global _container
    with _container_lock:
        _container = container

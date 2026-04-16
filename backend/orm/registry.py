"""
Registry - Central registry for dynamic models.

Maintains a mapping of all registered models and their fields.
"""

from typing import Dict, Optional, List, Type
import logging

logger = logging.getLogger(__name__)


class Registry:
    """Central registry for all dynamic models."""

    def __init__(self):
        self.models: Dict[str, "DynamicModel"] = {}
        self.fields: Dict[str, Dict[str, any]] = {}
        self.relations: Dict[str, List[Dict]] = {}

    def register_model(self, model_name: str, model_class: "DynamicModel"):
        """Register a dynamic model."""
        self.models[model_name] = model_class
        logger.info(f"[Registry] Registered model: {model_name}")

    def unregister_model(self, model_name: str):
        """Unregister a dynamic model."""
        if model_name in self.models:
            del self.models[model_name]
            logger.info(f"[Registry] Unregistered model: {model_name}")

    def get_model(self, model_name: str) -> Optional["DynamicModel"]:
        """Get a registered model by name."""
        return self.models.get(model_name)

    def register_fields(self, model_name: str, fields: Dict[str, any]):
        """Register fields for a model."""
        self.fields[model_name] = fields
        logger.debug(f"[Registry] Registered {len(fields)} fields for {model_name}")

    def get_fields(self, model_name: str) -> Dict[str, any]:
        """Get fields for a model."""
        return self.fields.get(model_name, {})

    def register_relation(self, model_name: str, relation: Dict):
        """Register a relation for a model."""
        if model_name not in self.relations:
            self.relations[model_name] = []
        self.relations[model_name].append(relation)

    def get_relations(self, model_name: str) -> List[Dict]:
        """Get all relations for a model."""
        return self.relations.get(model_name, [])

    def get_all_models(self) -> List[str]:
        """Get all registered model names."""
        return list(self.models.keys())

    def clear(self):
        """Clear all registrations (mainly for testing)."""
        self.models.clear()
        self.fields.clear()
        self.relations.clear()


# Global registry instance
registry = Registry()


def get_registry() -> Registry:
    """Get the global registry instance."""
    return registry

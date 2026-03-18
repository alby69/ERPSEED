"""
Builder Models - Archetype, Component, Block

DEPRECATED: This module is kept for backward compatibility.
New code should use: from backend.builder_service.infrastructure.persistence.builder_models import ...

This module re-exports from the new location.
"""

from backend.builder_service.infrastructure.persistence.builder_models import (
    Archetype,
    Component,
    Block,
    BlockRelationship,
    create_system_archetypes,
)

__all__ = ["Archetype", "Component", "Block", "BlockRelationship", "create_system_archetypes"]

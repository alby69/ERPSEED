"""
Capability Registry - Core system for AgentMesh integration.
Allows modules to register their CQRS Commands/Queries as Agent Tools.
"""

import logging
import inspect
from typing import Dict, List, Any, Optional, Type, Callable
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)

@dataclass
class Capability:
    """Represents a capability (tool) of an agent."""
    name: str
    description: str
    command_class: Type
    agent_name: str
    input_schema: Dict[str, Any] = field(default_factory=dict)
    category: str = "general"
    is_public: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "agent": self.agent_name,
            "input_schema": self.input_schema,
            "category": self.category,
            "command_class": self.command_class.__name__
        }

class CapabilityRegistry:
    """Central registry for all system capabilities."""

    def __init__(self):
        self._capabilities: Dict[str, Capability] = {}
        self._agents: Dict[str, List[str]] = {}

    def register(
        self,
        name: str,
        description: str,
        command_class: Type,
        agent_name: str,
        input_schema: Optional[Dict[str, Any]] = None,
        category: str = "general"
    ):
        """Registers a new capability."""
        if not input_schema:
            input_schema = self._generate_schema_from_command(command_class)

        capability = Capability(
            name=name,
            description=description,
            command_class=command_class,
            agent_name=agent_name,
            input_schema=input_schema,
            category=category
        )

        self._capabilities[name] = capability

        if agent_name not in self._agents:
            self._agents[agent_name] = []

        if name not in self._agents[agent_name]:
            self._agents[agent_name].append(name)

        logger.info(f"Registered capability: {name} for agent {agent_name}")

    def get_capability(self, name: str) -> Optional[Capability]:
        """Retrieves a capability by name."""
        return self._capabilities.get(name)

    def get_all_capabilities(self) -> List[Capability]:
        """Returns all registered capabilities."""
        return list(self._capabilities.values())

    def get_agent_capabilities(self, agent_name: str) -> List[Capability]:
        """Returns all capabilities for a specific agent."""
        cap_names = self._agents.get(agent_name, [])
        return [self._capabilities[name] for name in cap_names]

    def get_agents(self) -> List[str]:
        """Returns list of registered agents."""
        return list(self._agents.keys())

    def _generate_schema_from_command(self, command_class: Type) -> Dict[str, Any]:
        """
        Infers JSON Schema from a dataclass command.
        This is a simplified version, can be enhanced with pydantic or marshmallow.
        """
        properties = {}
        required = []

        # Get type hints
        import typing
        hints = typing.get_type_hints(command_class)

        # Get fields from dataclass
        import dataclasses
        for f in dataclasses.fields(command_class):
            if f.name in ['command_id', 'timestamp', 'tenant_id', 'userId', 'metadata']:
                continue

            field_type = hints.get(f.name, str)

            # Simple mapping
            type_name = "string"
            if field_type == int:
                type_name = "integer"
            elif field_type == float:
                type_name = "number"
            elif field_type == bool:
                type_name = "boolean"
            elif field_type == list or typing.get_origin(field_type) == list:
                type_name = "array"
            elif field_type == dict or typing.get_origin(field_type) == dict:
                type_name = "object"

            properties[f.name] = {
                "type": type_name,
                "description": f.name.replace('_', ' ').title()
            }

            # If no default value, mark as required (simplified logic)
            if f.default == dataclasses.MISSING and f.default_factory == dataclasses.MISSING:
                required.append(f.name)

        return {
            "type": "object",
            "properties": properties,
            "required": required
        }

# Global singleton
capability_registry = CapabilityRegistry()

def capability(name: str, description: str, agent: str, category: str = "general"):
    """Decorator to register a command as a capability."""
    def decorator(cls):
        capability_registry.register(
            name=name,
            description=description,
            command_class=cls,
            agent_name=agent,
            category=category
        )
        return cls
    return decorator

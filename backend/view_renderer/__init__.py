"""
View Renderer - Renders views based on configuration.

This module provides the base infrastructure for rendering dynamic views
based on SysView, SysComponent, and SysAction configurations.
"""

import json
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class ComponentConfig:
    """Configuration for a single component instance."""

    component_type: str
    props: Dict[str, Any] = field(default_factory=dict)
    children: List["ComponentConfig"] = field(default_factory=list)
    condition: Optional[str] = None


@dataclass
class ViewConfig:
    """Complete view configuration."""

    view_type: str
    model: str
    components: List[ComponentConfig] = field(default_factory=list)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)


class ViewRenderer:
    """Base class for rendering views from configuration.

    The ViewRenderer takes a ViewConfig and converts it into
    renderable data for the frontend.
    """

    def __init__(self):
        self.component_registry = None

    def set_registry(self, registry):
        """Set the component registry."""
        self.component_registry = registry

    def render(self, view_config: ViewConfig) -> Dict[str, Any]:
        """Render a view configuration to a dictionary.

        Args:
            view_config: The ViewConfig to render

        Returns:
            Dictionary representation of the view ready for the frontend
        """
        return {
            "viewType": view_config.view_type,
            "model": view_config.model,
            "components": self._render_components(view_config.components),
            "actions": view_config.actions,
            "config": view_config.config,
        }

    def _render_components(
        self, components: List[ComponentConfig]
    ) -> List[Dict[str, Any]]:
        """Render a list of components."""
        result = []
        for comp in components:
            rendered = self._render_component(comp)
            if rendered:
                result.append(rendered)
        return result

    def _render_component(self, comp: ComponentConfig) -> Optional[Dict[str, Any]]:
        """Render a single component."""
        if self.component_registry:
            component_def = self.component_registry.get(comp.component_type)
            if not component_def:
                return None

        return {
            "type": comp.component_type,
            "props": comp.props,
            "children": self._render_components(comp.children),
        }

    @staticmethod
    def from_json(json_str: str) -> ViewConfig:
        """Create a ViewConfig from JSON string."""
        data = json.loads(json_str)
        return ViewRenderer.parse_dict(data)

    @staticmethod
    def parse_dict(data: Dict[str, Any]) -> ViewConfig:
        """Parse a dictionary into a ViewConfig."""
        components = []
        for comp_data in data.get("components", []):
            components.append(ComponentConfigParser.parse(comp_data))

        return ViewConfig(
            view_type=data.get("viewType", "list"),
            model=data.get("model", ""),
            components=components,
            actions=data.get("actions", []),
            config=data.get("config", {}),
        )


class ComponentConfigParser:
    """Parser for component configuration."""

    @staticmethod
    def parse(data: Dict[str, Any]) -> ComponentConfig:
        """Parse a component from dictionary."""
        children = []
        for child_data in data.get("children", []):
            children.append(ComponentConfigParser.parse(child_data))

        return ComponentConfig(
            component_type=data.get("type", ""),
            props=data.get("props", {}),
            children=children,
            condition=data.get("condition"),
        )


def create_view_config(
    view_type: str,
    model: str,
    components: Optional[List[Dict]] = None,
    actions: Optional[List[Dict]] = None,
    **config,
) -> ViewConfig:
    """Helper function to create a ViewConfig."""
    return ViewConfig(
        view_type=view_type,
        model=model,
        components=[
            ComponentConfigParser.parse(c) if isinstance(c, dict) else c
            for c in (components or [])
        ],
        actions=actions or [],
        config=config,
    )


from .component_registry import get_registry, ComponentRegistry, ComponentDefinition

"""
Component Registry - Manages available UI components.

This module provides a registry for all available UI components
that can be used in views.
"""

import json
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field


@dataclass
class ComponentDefinition:
    """Definition of a UI component."""

    technical_name: str
    title: str
    component_type: str
    icon: str
    default_props: Dict[str, Any] = field(default_factory=dict)
    props_schema: Dict[str, Any] = field(default_factory=dict)
    component_path: str = ""
    description: str = ""
    category: str = "basic"


class ComponentRegistry:
    """Registry for all available UI components.

    The registry maintains a list of all components that can be used
    in views, along with their configurations and schemas.
    """

    def __init__(self):
        self._components: Dict[str, ComponentDefinition] = {}
        self._register_default_components()

    def _register_default_components(self):
        """Register default built-in components."""
        default_components = [
            ComponentDefinition(
                technical_name="table",
                title="Table",
                component_type="data",
                icon="table",
                component_path="@/components/Table",
                description="Data table with columns, sorting, and filtering",
                category="data",
                default_props={
                    "columns": [],
                    "pagination": True,
                    "pageSize": 20,
                    "rowSelection": True,
                },
                props_schema={
                    "type": "object",
                    "properties": {
                        "columns": {"type": "array"},
                        "pagination": {"type": "boolean"},
                        "pageSize": {"type": "number"},
                        "rowSelection": {"type": "boolean"},
                    },
                },
            ),
            ComponentDefinition(
                technical_name="form",
                title="Form",
                component_type="data",
                icon="form",
                component_path="@/components/Form",
                description="Dynamic form based on model fields",
                category="data",
                default_props={
                    "layout": "vertical",
                    "showActions": True,
                },
                props_schema={
                    "type": "object",
                    "properties": {
                        "layout": {
                            "type": "string",
                            "enum": ["vertical", "horizontal"],
                        },
                        "showActions": {"type": "boolean"},
                    },
                },
            ),
            ComponentDefinition(
                technical_name="kanban",
                title="Kanban",
                component_type="data",
                icon="columns",
                component_path="@/components/Kanban",
                description="Kanban board with drag-drop cards",
                category="data",
                default_props={
                    "groupBy": "state",
                    "showAddCard": True,
                },
                props_schema={
                    "type": "object",
                    "properties": {
                        "groupBy": {"type": "string"},
                        "showAddCard": {"type": "boolean"},
                    },
                },
            ),
            ComponentDefinition(
                technical_name="calendar",
                title="Calendar",
                component_type="data",
                icon="calendar",
                component_path="@/components/Calendar",
                description="Calendar view for scheduling",
                category="data",
                default_props={
                    "startDateField": "date",
                    "endDateField": "end_date",
                    "titleField": "name",
                },
                props_schema={
                    "type": "object",
                    "properties": {
                        "startDateField": {"type": "string"},
                        "endDateField": {"type": "string"},
                        "titleField": {"type": "string"},
                    },
                },
            ),
            ComponentDefinition(
                technical_name="chart",
                title="Chart",
                component_type="chart",
                icon="chart",
                component_path="@/components/Chart",
                description="Visualization chart (bar, line, pie, etc.)",
                category="chart",
                default_props={
                    "chartType": "bar",
                    "xAxis": "",
                    "yAxis": "",
                    "aggregation": "count",
                },
                props_schema={
                    "type": "object",
                    "properties": {
                        "chartType": {
                            "type": "string",
                            "enum": ["bar", "line", "pie", "area", "radar"],
                        },
                        "xAxis": {"type": "string"},
                        "yAxis": {"type": "string"},
                        "aggregation": {
                            "type": "string",
                            "enum": ["sum", "avg", "count", "min", "max"],
                        },
                    },
                },
            ),
            ComponentDefinition(
                technical_name="text",
                title="Text",
                component_type="basic",
                icon="text",
                component_path="@/components/Basic/Text",
                description="Simple text display",
                category="basic",
                default_props={
                    "content": "",
                    "variant": "body",
                },
                props_schema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "variant": {
                            "type": "string",
                            "enum": ["h1", "h2", "h3", "h4", "body", "small"],
                        },
                    },
                },
            ),
            ComponentDefinition(
                technical_name="heading",
                title="Heading",
                component_type="basic",
                icon="heading",
                component_path="@/components/Basic/Heading",
                description="Heading text element",
                category="basic",
                default_props={
                    "content": "",
                    "level": 1,
                },
                props_schema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "level": {"type": "number", "minimum": 1, "maximum": 6},
                    },
                },
            ),
            ComponentDefinition(
                technical_name="badge",
                title="Badge",
                component_type="basic",
                icon="badge",
                component_path="@/components/Basic/Badge",
                description="Status badge or tag",
                category="basic",
                default_props={
                    "text": "",
                    "color": "blue",
                },
                props_schema={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "color": {"type": "string"},
                    },
                },
            ),
            ComponentDefinition(
                technical_name="image",
                title="Image",
                component_type="basic",
                icon="image",
                component_path="@/components/Basic/Image",
                description="Image display",
                category="basic",
                default_props={
                    "src": "",
                    "alt": "",
                    "width": "100%",
                },
                props_schema={
                    "type": "object",
                    "properties": {
                        "src": {"type": "string"},
                        "alt": {"type": "string"},
                        "width": {"type": "string"},
                    },
                },
            ),
            ComponentDefinition(
                technical_name="tabs",
                title="Tabs",
                component_type="layout",
                icon="tabs",
                component_path="@/components/Layout/Tabs",
                description="Tabbed content container",
                category="layout",
                default_props={
                    "tabs": [],
                    "defaultTab": 0,
                },
                props_schema={
                    "type": "object",
                    "properties": {
                        "tabs": {"type": "array"},
                        "defaultTab": {"type": "number"},
                    },
                },
            ),
            ComponentDefinition(
                technical_name="accordion",
                title="Accordion",
                component_type="layout",
                icon="unordered-list",
                component_path="@/components/Layout/Accordion",
                description="Collapsible content sections",
                category="layout",
                default_props={
                    "items": [],
                    "allowMultiple": False,
                },
                props_schema={
                    "type": "object",
                    "properties": {
                        "items": {"type": "array"},
                        "allowMultiple": {"type": "boolean"},
                    },
                },
            ),
            ComponentDefinition(
                technical_name="modal",
                title="Modal",
                component_type="layout",
                icon="modal",
                component_path="@/components/Layout/Modal",
                description="Modal dialog",
                category="layout",
                default_props={
                    "title": "",
                    "size": "medium",
                    "closable": True,
                },
                props_schema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "size": {
                            "type": "string",
                            "enum": ["small", "medium", "large"],
                        },
                        "closable": {"type": "boolean"},
                    },
                },
            ),
            ComponentDefinition(
                technical_name="drawer",
                title="Drawer",
                component_type="layout",
                icon="drawer",
                component_path="@/components/Layout/Drawer",
                description="Slide-out panel",
                category="layout",
                default_props={
                    "title": "",
                    "placement": "right",
                    "width": 400,
                },
                props_schema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "placement": {
                            "type": "string",
                            "enum": ["top", "bottom", "left", "right"],
                        },
                        "width": {"type": "number"},
                    },
                },
            ),
            ComponentDefinition(
                technical_name="button",
                title="Button",
                component_type="basic",
                icon="button",
                component_path="@/components/Basic/Button",
                description="Interactive button",
                category="basic",
                default_props={
                    "text": "",
                    "variant": "primary",
                    "action": "",
                },
                props_schema={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "variant": {
                            "type": "string",
                            "enum": ["primary", "secondary", "danger", "link"],
                        },
                        "action": {"type": "string"},
                    },
                },
            ),
            ComponentDefinition(
                technical_name="filter",
                title="Filter",
                component_type="data",
                icon="filter",
                component_path="@/components/Filter",
                description="Filter panel for list views",
                category="data",
                default_props={
                    "fields": [],
                    "showSearch": True,
                },
                props_schema={
                    "type": "object",
                    "properties": {
                        "fields": {"type": "array"},
                        "showSearch": {"type": "boolean"},
                    },
                },
            ),
        ]

        for comp in default_components:
            self.register(comp)

    def register(self, component: ComponentDefinition):
        """Register a component."""
        self._components[component.technical_name] = component

    def get(self, technical_name: str) -> Optional[ComponentDefinition]:
        """Get a component by technical name."""
        return self._components.get(technical_name)

    def get_all(self) -> List[ComponentDefinition]:
        """Get all registered components."""
        return list(self._components.values())

    def get_by_category(self, category: str) -> List[ComponentDefinition]:
        """Get components by category."""
        return [c for c in self._components.values() if c.component_type == category]

    def get_categories(self) -> List[str]:
        """Get all available categories."""
        return list(set(c.component_type for c in self._components.values()))

    def to_dict(self) -> List[Dict[str, Any]]:
        """Export all components as dictionary list."""
        return [
            {
                "technicalName": c.technical_name,
                "title": c.title,
                "type": c.component_type,
                "icon": c.icon,
                "path": c.component_path,
                "description": c.description,
                "category": c.category,
                "defaultProps": c.default_props,
                "propsSchema": c.props_schema,
            }
            for c in self._components.values()
        ]

    @classmethod
    def from_database(cls, sys_components: List[Any]) -> "ComponentRegistry":
        """Create registry from database SysComponent records."""
        registry = cls()
        registry._components.clear()

        for sys_comp in sys_components:
            default_config = {}
            props_schema = {}

            if sys_comp.default_config:
                try:
                    default_config = json.loads(sys_comp.default_config)
                except (json.JSONDecodeError, TypeError):
                    pass

            if sys_comp.props_schema:
                try:
                    props_schema = json.loads(sys_comp.props_schema)
                except (json.JSONDecodeError, TypeError):
                    pass

            component = ComponentDefinition(
                technical_name=sys_comp.technical_name,
                title=sys_comp.title or sys_comp.name,
                component_type=sys_comp.component_type,
                icon=sys_comp.icon or "component",
                component_path=sys_comp.component_path or "",
                description=sys_comp.description or "",
                category=sys_comp.component_type,
                default_props=default_config,
                props_schema=props_schema,
            )
            registry.register(component)

        return registry


_global_registry: Optional[ComponentRegistry] = None


def get_registry() -> ComponentRegistry:
    """Get the global component registry."""
    global _global_registry
    if _global_registry is None:
        _global_registry = ComponentRegistry()
    return _global_registry


def register_component(component: ComponentDefinition):
    """Register a component in the global registry."""
    get_registry().register(component)

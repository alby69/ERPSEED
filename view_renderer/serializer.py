"""
View Config Serializer/Deserializer.

Handles conversion between database models (SysView, SysAction)
and runtime view configurations.
"""

import json
from typing import Any, Dict, List, Optional, Union
from dataclasses import asdict

from models import SysView, SysComponent, SysAction
from view_renderer import ViewConfig, ComponentConfig, ViewRenderer


class ViewConfigSerializer:
    """Serializes and deserializes view configurations."""

    @staticmethod
    def serialize_config(config: Dict[str, Any]) -> str:
        """Serialize a config dict to JSON string."""
        return json.dumps(config, default=str)

    @staticmethod
    def deserialize_config(config_str: str) -> Dict[str, Any]:
        """Deserialize JSON string to config dict."""
        if not config_str:
            return {}
        try:
            return json.loads(config_str)
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def sys_view_to_config(sys_view: SysView) -> ViewConfig:
        """Convert a SysView database model to a ViewConfig."""
        config = ViewConfigSerializer.deserialize_config(sys_view.config)
        components_data = config.get("components", [])

        from view_renderer import ComponentConfigParser

        parsed_components = []
        for comp_data in components_data:
            if isinstance(comp_data, dict):
                parsed_components.append(ComponentConfigParser.parse(comp_data))

        return ViewConfig(
            view_type=sys_view.view_type,
            model=f"{sys_view.model_id}" if sys_view.model_id else "",
            components=parsed_components,
            actions=config.get("actions", []),
            config=config,
        )

    @staticmethod
    def config_to_sys_view(
        view_config: ViewConfig,
        name: str,
        technical_name: str,
        view_type: str,
        model_id: int,
        title: Optional[str] = None,
        is_default: bool = False,
    ) -> Dict[str, Any]:
        """Convert a ViewConfig to a dictionary suitable for SysView."""
        config = {
            "components": [
                {
                    "type": comp.component_type,
                    "props": comp.props,
                    "condition": comp.condition,
                }
                for comp in view_config.components
            ],
            "actions": view_config.actions,
            **view_config.config,
        }

        return {
            "name": name,
            "technical_name": technical_name,
            "title": title or name,
            "view_type": view_type,
            "model_id": model_id,
            "config": ViewConfigSerializer.serialize_config(config),
            "is_default": is_default,
        }


class ActionSerializer:
    """Serializes and deserializes action configurations."""

    @staticmethod
    def serialize_action(action_config: Dict[str, Any]) -> str:
        """Serialize action config to JSON string."""
        return json.dumps(action_config, default=str)

    @staticmethod
    def deserialize_action(action_str: str) -> Dict[str, Any]:
        """Deserialize JSON string to action config."""
        if not action_str:
            return {}
        try:
            return json.loads(action_str)
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def sys_action_to_config(sys_action: SysAction) -> Dict[str, Any]:
        """Convert a SysAction to a dictionary."""
        config = ActionSerializer.deserialize_action(sys_action.config)
        conditions = ActionSerializer.deserialize_action(sys_action.conditions)

        return {
            "id": sys_action.id,
            "name": sys_action.name,
            "technicalName": sys_action.technical_name,
            "title": sys_action.title,
            "type": sys_action.action_type,
            "target": sys_action.target,
            "icon": sys_action.icon,
            "style": sys_action.style,
            "position": sys_action.position,
            "config": config,
            "conditions": conditions,
            "order": sys_action.order,
        }

    @staticmethod
    def config_to_sys_action(
        action_config: Dict[str, Any],
        name: str,
        technical_name: str,
        action_type: str,
        target: str,
        view_id: Optional[int] = None,
        model_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Convert action config dictionary to SysAction data."""
        return {
            "name": name,
            "technical_name": technical_name,
            "title": action_config.get("title", name),
            "action_type": action_type,
            "target": target,
            "view_id": view_id,
            "model_id": model_id,
            "config": ActionSerializer.serialize_action(
                action_config.get("config", {})
            ),
            "icon": action_config.get("icon"),
            "style": action_config.get("style", "primary"),
            "position": action_config.get("position", "toolbar"),
            "conditions": ActionSerializer.serialize_action(
                action_config.get("conditions", {})
            ),
            "order": action_config.get("order", 0),
        }


class ComponentSerializer:
    """Serializes and deserializes component configurations."""

    @staticmethod
    def serialize_props(props: Dict[str, Any]) -> str:
        """Serialize component props to JSON string."""
        return json.dumps(props, default=str)

    @staticmethod
    def deserialize_props(props_str: str) -> Dict[str, Any]:
        """Deserialize JSON string to component props."""
        if not props_str:
            return {}
        try:
            return json.loads(props_str)
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def sys_component_to_def(sys_component: SysComponent) -> Dict[str, Any]:
        """Convert a SysComponent to a component definition."""
        default_config = ComponentSerializer.deserialize_props(
            sys_component.default_config
        )
        props_schema = ComponentSerializer.deserialize_props(sys_component.props_schema)

        return {
            "technicalName": sys_component.technical_name,
            "title": sys_component.title or sys_component.name,
            "type": sys_component.component_type,
            "icon": sys_component.icon,
            "path": sys_component.component_path,
            "description": sys_component.description,
            "defaultProps": default_config,
            "propsSchema": props_schema,
            "isCustom": sys_component.is_custom,
        }

    @staticmethod
    def def_to_sys_component(
        component_def: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Convert a component definition to SysComponent data."""
        return {
            "name": component_def.get("title", component_def.get("technicalName")),
            "technical_name": component_def.get("technicalName"),
            "title": component_def.get("title"),
            "description": component_def.get("description", ""),
            "component_type": component_def.get("type", "custom"),
            "component_path": component_def.get("path", ""),
            "default_config": ComponentSerializer.serialize_props(
                component_def.get("defaultProps", {})
            ),
            "props_schema": ComponentSerializer.serialize_props(
                component_def.get("propsSchema", {})
            ),
            "icon": component_def.get("icon", "component"),
            "is_custom": True,
        }


def serialize_view_for_frontend(
    sys_view: SysView,
    actions: Optional[List[SysAction]] = None,
) -> Dict[str, Any]:
    """Serialize a SysView for frontend consumption.

    This is the main entry point for the API to return view data.
    """
    config = ViewConfigSerializer.deserialize_config(sys_view.config)
    components = config.get("components", [])
    view_config = config.get("config", {})

    serialized_actions = []
    if actions:
        serialized_actions = [
            ActionSerializer.sys_action_to_config(action) for action in actions
        ]

    return {
        "id": sys_view.id,
        "name": sys_view.name,
        "technicalName": sys_view.technical_name,
        "title": sys_view.title,
        "viewType": sys_view.view_type,
        "modelId": sys_view.model_id,
        "isDefault": sys_view.is_default,
        "order": sys_view.order,
        "components": components,
        "actions": serialized_actions,
        "config": view_config,
    }


def deserialize_view_from_frontend(
    data: Dict[str, Any],
    model_id: int,
) -> Dict[str, Any]:
    """Deserialize view data from frontend to SysView format.

    This is the main entry point for creating/updating views from API input.
    """
    view_config = data.get("config", {})
    components = data.get("components", [])

    full_config = {
        "components": components,
        "actions": data.get("actions", []),
        "config": view_config,
    }

    return {
        "name": data.get("name"),
        "technical_name": data.get("technicalName", data.get("name")),
        "title": data.get("title", data.get("name")),
        "view_type": data.get("viewType", "list"),
        "model_id": model_id,
        "config": ViewConfigSerializer.serialize_config(full_config),
        "is_default": data.get("isDefault", False),
        "is_active": data.get("isActive", True),
        "order": data.get("order", 0),
    }

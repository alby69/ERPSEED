"""
Seed metadata for SysComponent and SysAction.
Populates the database with standard UI components and actions.
"""
import json
from . import create_app
from extensions import db
from models import SysComponent, SysAction

def seed_metadata():
    print("Seeding metadata (SysComponent and SysAction)...")
    app = create_app()

    with app.app_context():
        # 1. Seed SysComponents
        print("Seeding SysComponents...")

        # Check if they already exist to avoid duplicates
        existing_components = {c.technical_name for c in SysComponent.query.all()}

        default_components = [
            {
                "technical_name": "table",
                "name": "Table",
                "title": "Data Table",
                "component_type": "data",
                "icon": "table",
                "component_path": "@/components/Table",
                "description": "Data table with columns, sorting, and filtering",
                "default_config": {
                    "columns": [],
                    "pagination": True,
                    "pageSize": 20,
                    "rowSelection": True,
                },
                "props_schema": {
                    "type": "object",
                    "properties": {
                        "columns": {"type": "array", "title": "Columns"},
                        "pagination": {"type": "boolean", "title": "Enable Pagination"},
                        "pageSize": {"type": "number", "title": "Page Size"},
                        "rowSelection": {"type": "boolean", "title": "Enable Row Selection"},
                    },
                },
            },
            {
                "technical_name": "form",
                "name": "Form",
                "title": "Dynamic Form",
                "component_type": "data",
                "icon": "form",
                "component_path": "@/components/Form",
                "description": "Dynamic form based on model fields",
                "default_config": {
                    "layout": "vertical",
                    "showActions": True,
                },
                "props_schema": {
                    "type": "object",
                    "properties": {
                        "layout": {
                            "type": "string",
                            "enum": ["vertical", "horizontal"],
                            "title": "Layout",
                        },
                        "showActions": {"type": "boolean", "title": "Show Action Buttons"},
                    },
                },
            },
            {
                "technical_name": "kanban",
                "name": "Kanban",
                "title": "Kanban Board",
                "component_type": "data",
                "icon": "columns",
                "component_path": "@/components/Kanban",
                "description": "Kanban board with drag-drop cards",
                "default_config": {
                    "groupBy": "status",
                    "showAddCard": True,
                },
                "props_schema": {
                    "type": "object",
                    "properties": {
                        "groupBy": {"type": "string", "title": "Group By Field"},
                        "showAddCard": {"type": "boolean", "title": "Show Add Button"},
                    },
                },
            },
            {
                "technical_name": "chart",
                "name": "Chart",
                "title": "Data Visualization",
                "component_type": "chart",
                "icon": "bar-chart",
                "component_path": "@/components/Chart",
                "description": "Visualization chart (bar, line, pie, etc.)",
                "default_config": {
                    "chartType": "bar",
                    "xAxis": "",
                    "yAxis": "",
                    "aggregation": "count",
                },
                "props_schema": {
                    "type": "object",
                    "properties": {
                        "chartType": {
                            "type": "string",
                            "enum": ["bar", "line", "pie", "area", "radar"],
                            "title": "Chart Type",
                        },
                        "xAxis": {"type": "string", "title": "X-Axis Field"},
                        "yAxis": {"type": "string", "title": "Y-Axis Field"},
                        "aggregation": {
                            "type": "string",
                            "enum": ["sum", "avg", "count", "min", "max"],
                            "title": "Aggregation",
                        },
                    },
                },
            },
            {
                "technical_name": "text",
                "name": "Text",
                "title": "Text Label",
                "component_type": "basic",
                "icon": "font-size",
                "component_path": "@/components/Basic/Text",
                "description": "Simple text display",
                "default_config": {
                    "content": "Sample Text",
                    "variant": "body",
                },
                "props_schema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "title": "Content"},
                        "variant": {
                            "type": "string",
                            "enum": ["h1", "h2", "h3", "h4", "body", "small"],
                            "title": "Typography Variant",
                        },
                    },
                },
            },
            {
                "technical_name": "badge",
                "name": "Badge",
                "title": "Status Badge",
                "component_type": "basic",
                "icon": "tag",
                "component_path": "@/components/Basic/Badge",
                "description": "Status or count badge",
                "default_config": {
                    "count": 0,
                    "color": "blue",
                    "status": "default",
                },
                "props_schema": {
                    "type": "object",
                    "properties": {
                        "count": {"type": "number", "title": "Count"},
                        "color": {"type": "string", "title": "Color"},
                        "status": {
                            "type": "string",
                            "enum": ["success", "processing", "default", "error", "warning"],
                            "title": "Status",
                        },
                    },
                },
            },
            {
                "technical_name": "richtext",
                "name": "RichText",
                "title": "Rich Text Editor",
                "component_type": "advanced",
                "icon": "edit",
                "component_path": "@/components/Advanced/RichText",
                "description": "WYSIWYG editor for rich content",
                "default_config": {
                    "placeholder": "Enter content here...",
                    "height": 300,
                },
                "props_schema": {
                    "type": "object",
                    "properties": {
                        "placeholder": {"type": "string", "title": "Placeholder"},
                        "height": {"type": "number", "title": "Height (px)"},
                    },
                },
            },
            {
                "technical_name": "fileupload",
                "name": "FileUpload",
                "title": "File Upload",
                "component_type": "advanced",
                "icon": "upload",
                "component_path": "@/components/Advanced/FileUpload",
                "description": "Drag & drop file upload component",
                "default_config": {
                    "multiple": False,
                    "maxSize": 10,
                    "accept": "*",
                },
                "props_schema": {
                    "type": "object",
                    "properties": {
                        "multiple": {"type": "boolean", "title": "Allow Multiple"},
                        "maxSize": {"type": "number", "title": "Max Size (MB)"},
                        "accept": {"type": "string", "title": "Accepted Formats"},
                    },
                },
            },
            {
                "technical_name": "tabs",
                "name": "Tabs",
                "title": "Tab Container",
                "component_type": "layout",
                "icon": "folder",
                "component_path": "@/components/Layout/Tabs",
                "description": "Tabbed container for organizing components",
                "default_config": {
                    "items": [{"label": "Tab 1", "key": "1"}],
                    "type": "line",
                },
                "props_schema": {
                    "type": "object",
                    "properties": {
                        "items": {
                            "type": "array",
                            "title": "Tab Items",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "label": {"type": "string"},
                                    "key": {"type": "string"},
                                }
                            }
                        },
                        "type": {
                            "type": "string",
                            "enum": ["line", "card", "editable-card"],
                            "title": "Tab Style",
                        },
                    },
                },
            }
        ]

        for comp_data in default_components:
            if comp_data["technical_name"] not in existing_components:
                comp = SysComponent(
                    technical_name=comp_data["technical_name"],
                    name=comp_data["name"],
                    title=comp_data["title"],
                    component_type=comp_data["component_type"],
                    icon=comp_data["icon"],
                    component_path=comp_data["component_path"],
                    description=comp_data["description"],
                    default_config=json.dumps(comp_data["default_config"]),
                    props_schema=json.dumps(comp_data["props_schema"]),
                    is_active=True,
                    is_custom=False
                )
                db.session.add(comp)

        # 2. Seed SysActions
        print("Seeding SysActions...")

        # Check if they already exist
        existing_actions = {a.technical_name for a in SysAction.query.filter_by(viewId=None).all()}

        default_actions = [
            {
                "technical_name": "save",
                "name": "Save",
                "title": "Save Record",
                "action_type": "button",
                "target": "api",
                "icon": "save",
                "style": "primary",
                "position": "toolbar",
                "config": {"method": "POST", "url": "/api/{{model}}/save"},
            },
            {
                "technical_name": "delete",
                "name": "Delete",
                "title": "Delete Record",
                "action_type": "button",
                "target": "api",
                "icon": "delete",
                "style": "danger",
                "position": "row",
                "config": {"method": "DELETE", "url": "/api/{{model}}/{{id}}"},
            },
            {
                "technical_name": "navigate",
                "name": "Navigate",
                "title": "Go to View",
                "action_type": "button",
                "target": "view",
                "icon": "arrow-right",
                "style": "default",
                "position": "row",
                "config": {"view_name": ""},
            }
        ]

        for act_data in default_actions:
            if act_data["technical_name"] not in existing_actions:
                act = SysAction(
                    technical_name=act_data["technical_name"],
                    name=act_data["name"],
                    title=act_data["title"],
                    action_type=act_data["action_type"],
                    target=act_data["target"],
                    icon=act_data["icon"],
                    style=act_data["style"],
                    position=act_data["position"],
                    config=json.dumps(act_data["config"]),
                    is_active=True
                )
                db.session.add(act)

        db.session.commit()
        print("Metadata seeding completed successfully!")

if __name__ == "__main__":
    seed_metadata()

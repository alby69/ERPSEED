"""
Visual Builder API - Dedicated endpoints for saving and loading UI views.
"""

import json
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from marshmallow import Schema, fields

from backend.extensions import db
from backend.models import SysView, SysAction, SysModel
from backend.infrastructure.view_renderer.serializer import (
    serialize_view_for_frontend,
    deserialize_view_from_frontend
)

blp = Blueprint(
    "visual_builder",
    __name__,
    url_prefix="/api/visual-builder",
    description="Dedicated Visual Builder API",
)

# === SCHEMAS ===

class ComponentConfigSchema(Schema):
    id = fields.String()
    type = fields.String(required=True)
    name = fields.String()
    x = fields.Integer()
    y = fields.Integer()
    w = fields.Integer()
    h = fields.Integer()
    config = fields.Dict()

class VisualBuilderSaveSchema(Schema):
    view_id = fields.Integer()
    project_id = fields.Integer(required=True)
    model_id = fields.Integer()
    name = fields.String(required=True)
    technical_name = fields.String()
    title = fields.String()
    view_type = fields.String(dump_default="custom")
    components = fields.List(fields.Nested(ComponentConfigSchema))
    actions = fields.List(fields.Dict())
    config = fields.Dict()
    is_default = fields.Boolean()

class VisualBuilderLoadResponseSchema(Schema):
    id = fields.Int()
    name = fields.String()
    technicalName = fields.String()
    title = fields.String()
    viewType = fields.String()
    isDefault = fields.Boolean()
    config = fields.Dict()
    components = fields.List(fields.Nested(ComponentConfigSchema))
    actions = fields.List(fields.Dict())
    model = fields.Dict(allow_none=True)

class VisualBuilderSaveResponseSchema(Schema):
    id = fields.Int()
    message = fields.String()
    technicalName = fields.String()

class SysComponentResponseSchema(Schema):
    id = fields.Int()
    technicalName = fields.String()
    name = fields.String()
    title = fields.String()
    type = fields.String()
    icon = fields.String()
    description = fields.String()
    defaultConfig = fields.Dict()
    propsSchema = fields.Dict()

# === ROUTES ===

@blp.route("/load/<int:view_id>")
class VisualBuilderLoad(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, VisualBuilderLoadResponseSchema)
    def get(self, view_id):
        """Load a view configuration with full metadata."""
        sys_view = SysView.query.get_or_404(view_id)

        # Get actions for this view
        actions = SysAction.query.filter_by(view_id=view_id).all()

        # Serialize view
        view_data = serialize_view_for_frontend(sys_view, actions)

        # Add model metadata if available
        if sys_view.model_id:
            model = SysModel.query.get(sys_view.model_id)
            if model:
                view_data["model"] = {
                    "id": model.id,
                    "name": model.name,
                    "technicalName": model.technical_name,
                    "title": model.title,
                    "fields": [
                        {
                            "id": f.id,
                            "name": f.name,
                            "technicalName": f.technical_name,
                            "type": f.type,
                            "title": f.title
                        } for f in model.fields
                    ]
                }

        return view_data

@blp.route("/save")
class VisualBuilderSave(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(VisualBuilderSaveSchema)
    @blp.response(201, VisualBuilderSaveResponseSchema)
    def post(self, view_data):
        """Save or update a view configuration."""
        view_id = view_data.get("view_id")
        model_id = view_data.get("model_id")

        if view_id:
            sys_view = SysView.query.get_or_404(view_id)
            # Update existing
            update_data = deserialize_view_from_frontend(view_data, model_id or sys_view.model_id)
            for key, value in update_data.items():
                setattr(sys_view, key, value)
        else:
            # Create new
            if not model_id:
                abort(400, message="model_id is required for new views")

            create_data = deserialize_view_from_frontend(view_data, model_id)
            sys_view = SysView(**create_data)
            db.session.add(sys_view)

        db.session.commit()

        return {
            "id": sys_view.id,
            "message": "View saved successfully",
            "technicalName": sys_view.technical_name
        }

@blp.route("/components")
class VisualBuilderComponents(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, SysComponentResponseSchema(many=True))
    def get(self):
        """List all available UI components from SysComponent."""
        from backend.models import SysComponent
        components = SysComponent.query.filter_by(is_active=True).all()

        return [
            {
                "id": c.id,
                "technicalName": c.technical_name,
                "name": c.name,
                "title": c.title,
                "type": c.component_type,
                "icon": c.icon,
                "description": c.description,
                "defaultConfig": json.loads(c.default_config) if c.default_config else {},
                "propsSchema": json.loads(c.props_schema) if c.props_schema else {}
            } for c in components
        ]

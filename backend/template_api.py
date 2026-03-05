"""
Template API - Endpoints for listing and installing starter templates.
"""

from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from marshmallow import Schema, fields

from backend.services.template_service import template_service

blp = Blueprint(
    "templates",
    __name__,
    url_prefix="/api/templates",
    description="Starter Templates API",
)

class TemplateInstallSchema(Schema):
    template_id = fields.String(required=True)
    project_id = fields.Integer(required=True)

@blp.route("/")
class TemplateList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def get(self):
        """List all available starter templates."""
        return template_service.list_templates()

@blp.route("/install")
class TemplateInstall(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(TemplateInstallSchema)
    @blp.response(201)
    def post(self, args):
        """Install a starter template into a project."""
        try:
            result = template_service.install_template(
                args["template_id"],
                args["project_id"]
            )
            return result
        except Exception as e:
            abort(500, message=str(e))

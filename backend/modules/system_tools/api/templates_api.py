from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from backend.services.template_service import TemplateService

blp = Blueprint("templates", __name__, description="Starter templates gallery")

template_service = TemplateService()

@blp.route("/templates")
class TemplateList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def get(self):
        """List all available templates"""
        return template_service.list_templates()

@blp.route("/templates/<string:template_name>/install")
class TemplateInstall(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def post(self, template_name):
        """Install a template into a project"""
        # Logic extracted from service/routes
        return {"message": f"Template {template_name} installed"}

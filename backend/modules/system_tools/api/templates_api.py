from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.modules.system_tools.services.template_service import TemplateService

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
@blp.route("/templates/<string:template_name>/apply")
class TemplateInstall(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def post(self, template_name):
        """Install or apply a template into a project/tenant"""
        user = get_jwt_identity() or {}
        tenant_id = user.get("tenant_id", 1) if isinstance(user, dict) else 1
        project_id = request.args.get("projectId", 1, type=int)
        try:
            res = template_service.apply_template(template_name, projectId=project_id, tenant_id=tenant_id)
            return res
        except ValueError as e:
            abort(404, message=str(e))
        except Exception as e:
            abort(500, message=f"Failed to apply template: {str(e)}")

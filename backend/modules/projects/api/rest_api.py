from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from flask import request
from marshmallow import Schema, fields
from backend.models import Project, SysModel
from backend.extensions import db
from backend.core.schemas.schemas import (
    ProjectSchema,
    ProjectUpdateSchema,
    SysModelSchema,
    SysModelCreateSchema,
    ProjectMemberSchema,
    UserDisplaySchema,
)
from backend.core.decorators.decorators import admin_required
from backend.core.utils.utils import paginate
from backend.modules.projects.service import get_project_service
from backend.core.services.generic_service import generic_service

blp = Blueprint(
    "projects", "projects", url_prefix="/projects", description="Operations on projects"
)

class FileUploadSchema(Schema):
    file = fields.Raw(metadata={"type": "file"}, required=True)

project_service = get_project_service()


@blp.route("")
class ProjectList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, ProjectSchema(many=True))
    def get(self):
        """List projects the user has access to"""
        userId = get_jwt_identity()
        projects = project_service.get_all_for_user(userId)
        items, headers = paginate(projects)
        return items, 200, headers

    @blp.doc(security=[{"jwt": []}])
    @admin_required()
    @blp.arguments(ProjectSchema)
    @blp.response(201, ProjectSchema)
    def post(self, project_data):
        """Create a new project (Admin only)"""
        owner_id = get_jwt_identity()

        return project_service.create(
            name=project_data.name,
            title=project_data.title,
            description=project_data.description,
            owner_id=owner_id,
        ), 201


@blp.route("/<int:projectId>")
class ProjectResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, ProjectSchema)
    def get(self, projectId):
        """Get project details by ID"""
        userId = get_jwt_identity()
        return project_service.get_by_id(projectId, userId)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(ProjectUpdateSchema)
    @blp.response(200, ProjectSchema)
    def put(self, update_data, projectId):
        """Update an existing project (Admin or Owner)"""
        userId = get_jwt_identity()
        return project_service.update(projectId, userId, update_data)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, projectId):
        """Delete a project (Admin or Owner)"""
        userId = get_jwt_identity()
        project_service.delete(projectId, userId)
        return ""


@blp.route("/<int:projectId>/models")
class ProjectModels(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, SysModelSchema(many=True))
    def get(self, projectId):
        """List models for a project.

        - Admins see all models (including draft) for Builder access
        - Regular users only see published models
        """
        from backend.models import User

        userId = get_jwt_identity()
        user = db.session.get(User, userId)

        project = project_service.get_by_id(projectId, userId)

        if user and user.role == "admin":
            return project.models
        else:
            return [m for m in project.models if m.status == "published"] # type: ignore

    @blp.doc(security=[{"jwt": []}])
    @admin_required()
    @blp.arguments(SysModelCreateSchema)
    @blp.response(201, SysModelSchema)
    def post(self, model_data, projectId):
        """Create a new model in a project (Admin only)"""
        project_service.get_by_id(projectId, get_jwt_identity())
        return generic_service.create_scoped_resource(
            SysModel, model_data, {'projectId': projectId}, unique_fields=['name']
        )


@blp.route("/<int:projectId>/members")
class ProjectMemberList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, UserDisplaySchema(many=True))
    def get(self, projectId):
        """List members of a project"""
        userId = get_jwt_identity()
        return project_service.get_members(projectId, userId)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(ProjectMemberSchema)
    @blp.response(201, UserDisplaySchema)
    def post(self, member_data, projectId):
        """Add a member to a project (Admin or Owner)"""
        userId = get_jwt_identity()
        member_userId = member_data["userId"]

        return project_service.add_member(projectId, userId, member_userId)


@blp.route("/<int:projectId>/members/<int:userId>")
class ProjectMemberResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, projectId, userId):
        """Remove a member from a project (Admin or Owner)"""
        current_userId = get_jwt_identity()
        project_service.remove_member(projectId, current_userId, userId)
        return ""


@blp.route("/<int:projectId>/export")
class ProjectExport(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @admin_required()
    @blp.response(200, content_type="application/json")
    def get(self, projectId):
        """Export project as JSON template"""
        project_service.get_by_id(projectId, get_jwt_identity())

        export_data = project_service.export_template(projectId)
        project = Project.query.get(projectId)
        filename = project.name if project else "project"
        headers = {"Content-Disposition": f"attachment; filename={filename}_template.json"}

        return export_data, 200, headers


@blp.route("/imports")
class ProjectImport(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @admin_required()
    @blp.arguments(FileUploadSchema, location="files")
    @blp.response(200)
    def post(self, files):
        """Import project from JSON template (Create or Update)"""
        file = files["file"]

        try:
            data = json.load(file.stream)
        except Exception as e:
            abort(400, message=f"Invalid JSON: {str(e)}")

        userId = get_jwt_identity()
        message, projectId = project_service.import_template(data, userId)

        return {"message": message, "projectId": projectId}, 200

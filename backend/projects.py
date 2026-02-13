from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from flask import make_response, request

from .models import Project, SysModel
from .extensions import db
from .schemas import ProjectSchema, ProjectUpdateSchema, SysModelSchema, SysModelCreateSchema, ProjectMemberSchema, UserDisplaySchema
from .decorators import admin_required
from .utils import paginate
from .services import ProjectService

blp = Blueprint("projects", "projects", url_prefix="/projects", description="Operations on projects")

project_service = ProjectService()


@blp.route("")
class ProjectList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, ProjectSchema(many=True))
    def get(self):
        """List projects the user has access to"""
        user_id = get_jwt_identity()
        projects = project_service.get_all_for_user(user_id)
        items, headers = paginate(projects)
        return items, 200, headers

    @blp.doc(security=[{"jwt": []}])
    @admin_required()
    @blp.arguments(ProjectSchema)
    @blp.response(201, ProjectSchema)
    def post(self, project_data):
        """Create a new project (Admin only)"""
        owner_id = get_jwt_identity()
        
        data = project_data.__dict__ if hasattr(project_data, '__dict__') else project_data
        
        return project_service.create(
            name=data['name'],
            title=data['title'],
            description=data.get('description'),
            owner_id=owner_id
        ), 201


@blp.route("/<int:project_id>")
class ProjectResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, ProjectSchema)
    def get(self, project_id):
        """Get project details by ID"""
        user_id = get_jwt_identity()
        return project_service.get_by_id(project_id, user_id)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(ProjectUpdateSchema)
    @blp.response(200, ProjectSchema)
    def put(self, update_data, project_id):
        """Update an existing project (Admin or Owner)"""
        user_id = get_jwt_identity()
        return project_service.update(project_id, user_id, update_data)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, project_id):
        """Delete a project (Admin or Owner)"""
        user_id = get_jwt_identity()
        project_service.delete(project_id, user_id)
        return ""


@blp.route("/<int:project_id>/models")
class ProjectModels(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, SysModelSchema(many=True))
    def get(self, project_id):
        """List all models for a project"""
        project = project_service.get_by_id(project_id, get_jwt_identity())
        return project.models

    @blp.doc(security=[{"jwt": []}])
    @admin_required()
    @blp.arguments(SysModelCreateSchema)
    @blp.response(201, SysModelSchema)
    def post(self, model_data, project_id):
        """Create a new model in a project (Admin only)"""
        project_service.get_by_id(project_id, get_jwt_identity())
        
        data = model_data.__dict__ if hasattr(model_data, '__dict__') else model_data
        
        existing = SysModel.query.filter_by(project_id=project_id, name=data['name']).first()
        if existing:
            abort(409, message=f"A model with name '{data['name']}' already exists in this project.")
        
        model = SysModel(project_id=project_id, **data)
        db.session.add(model)
        db.session.commit()
        return model


@blp.route("/<int:project_id>/members")
class ProjectMemberList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, UserDisplaySchema(many=True))
    def get(self, project_id):
        """List members of a project"""
        user_id = get_jwt_identity()
        return project_service.get_members(project_id, user_id)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(ProjectMemberSchema)
    @blp.response(201, UserDisplaySchema)
    def post(self, member_data, project_id):
        """Add a member to a project (Admin or Owner)"""
        user_id = get_jwt_identity()
        member_user_id = member_data['user_id']
        
        return project_service.add_member(project_id, user_id, member_user_id)


@blp.route("/<int:project_id>/members/<int:user_id>")
class ProjectMemberResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, project_id, user_id):
        """Remove a member from a project (Admin or Owner)"""
        current_user_id = get_jwt_identity()
        project_service.remove_member(project_id, current_user_id, user_id)
        return ""


@blp.route("/<int:project_id>/export")
class ProjectExport(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @admin_required()
    def get(self, project_id):
        """Export project as JSON template"""
        project_service.get_by_id(project_id, get_jwt_identity())
        
        export_data = project_service.export_template(project_id)
        
        response = make_response(json.dumps(export_data, indent=2))
        
        project = Project.query.get(project_id)
        response.headers["Content-Disposition"] = f"attachment; filename={project.name}_template.json"
        response.headers["Content-Type"] = "application/json"
        return response


@blp.route("/import")
class ProjectImport(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @admin_required()
    def post(self):
        """Import project from JSON template (Create or Update)"""
        if 'file' not in request.files:
            abort(400, message="No file part")
        
        file = request.files['file']
        if file.filename == '':
            abort(400, message="No selected file")
            
        try:
            data = json.load(file)
        except Exception as e:
            abort(400, message=f"Invalid JSON: {str(e)}")
        
        user_id = get_jwt_identity()
        message, project_id = project_service.import_template(data, user_id)
        
        return {"message": message, "project_id": project_id}, 200

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import Project
from .extensions import db
from .schemas import ProjectSchema
from .utils import apply_filters, paginate, apply_sorting

blp = Blueprint("projects", __name__, description="Operations on projects")

@blp.route("/projects")
class ProjectList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, ProjectSchema(many=True))
    def get(self):
        """List all projects"""
        query = Project.query
        query = apply_filters(query, Project, ['name', 'description'])
        query = apply_sorting(query, Project)
        items, headers = paginate(query)
        return items, 200, headers

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(ProjectSchema)
    @blp.response(201, ProjectSchema)
    def post(self, project_data):
        """Create a new project"""
        current_user_id = get_jwt_identity()
        project = Project(
            name=project_data["name"],
            description=project_data.get("description"),
            user_id=current_user_id
        )
        db.session.add(project)
        db.session.commit()
        return project

@blp.route("/projects/<int:project_id>")
class ProjectResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, ProjectSchema)
    def get(self, project_id):
        """Get a project by ID"""
        project = Project.query.get_or_404(project_id)
        return project

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(ProjectSchema)
    @blp.response(200, ProjectSchema)
    def put(self, project_data, project_id):
        """Update a project"""
        project = Project.query.get_or_404(project_id)
        project.name = project_data.get("name", project.name)
        project.description = project_data.get("description", project.description)
        db.session.commit()
        return project

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, project_id):
        """Delete a project"""
        project = Project.query.get_or_404(project_id)
        db.session.delete(project)
        db.session.commit()
        return ""
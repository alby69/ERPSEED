from .application.handlers import ProjectCommandHandler
from .application.commands.project_commands import CreateProjectCommand, UpdateProjectCommand, DeleteProjectCommand, AddMemberCommand, RemoveMemberCommand
from backend.models import User, Project
from backend.extensions import db
from flask_smorest import abort

class ProjectService:
    def __init__(self):
        self.handler = ProjectCommandHandler()

    def get_all_for_user(self, userId):
        user = db.session.get(User, int(userId))
        if not user:
            abort(404, message="User not found.")

        user_id_int = int(userId)
        if user.role == 'admin':
            return Project.query.order_by(Project.name)

        return Project.query.filter(
            (Project.owner_id == user_id_int) | (Project.members.any(id=user_id_int))
        ).order_by(Project.name)

    def get_by_id(self, projectId, userId):
        project = db.session.get(Project, projectId)
        if not project:
            abort(404, message="Project not found.")

        user = db.session.get(User, int(userId))
        user_id_int = int(userId)
        is_member = project.members.filter_by(id=user_id_int).first() is not None

        if user.role != 'admin' and project.owner_id != user_id_int and not is_member:
            abort(403, message="You don't have access to this project.")

        return project

    def create(self, name, title, description, owner_id):
        cmd = CreateProjectCommand(name, title, description, owner_id)
        return self.handler.handle_create(cmd)

    def update(self, projectId, userId, data):
        cmd = UpdateProjectCommand(projectId, userId, data)
        return self.handler.handle_update(cmd)

    def delete(self, projectId, userId):
        cmd = DeleteProjectCommand(projectId, userId)
        return self.handler.handle_delete(cmd)

    def add_member(self, projectId, userId, member_userId):
        cmd = AddMemberCommand(projectId, userId, member_userId)
        return self.handler.handle_add_member(cmd)

    def remove_member(self, projectId, userId, member_userId):
        cmd = RemoveMemberCommand(projectId, userId, member_userId)
        return self.handler.handle_remove_member(cmd)

    def get_members(self, projectId, userId):
        project = self.get_by_id(projectId, userId)
        return project.members.all()

_project_service = None

def get_project_service():
    global _project_service
    if _project_service is None:
        _project_service = ProjectService()
    return _project_service

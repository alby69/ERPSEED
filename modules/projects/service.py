from .application.handlers import ProjectCommandHandler
from .application.commands.project_commands import CreateProjectCommand, UpdateProjectCommand, DeleteProjectCommand, AddMemberCommand, RemoveMemberCommand
from models import User, Project
from extensions import db
from flask_smorest import abort

class ProjectService:
    def __init__(self):
        self.handler = ProjectCommandHandler()

    def get_all_for_user(self, user_id):
        user = db.session.get(User, user_id)
        if not user:
            abort(404, message="User not found.")

        if user.role == 'admin':
            return Project.query.order_by(Project.name)

        return Project.query.filter(
            (Project.owner_id == user_id) | (Project.members.any(id=user_id))
        ).order_by(Project.name)

    def get_by_id(self, project_id, user_id):
        project = db.session.get(Project, project_id)
        if not project:
            abort(404, message="Project not found.")

        user = db.session.get(User, user_id)
        is_member = project.members.filter_by(id=user_id).first() is not None

        if user.role != 'admin' and project.owner_id != user_id and not is_member:
            abort(403, message="You don't have access to this project.")

        return project

    def create(self, name, title, description, owner_id):
        cmd = CreateProjectCommand(name, title, description, owner_id)
        return self.handler.handle_create(cmd)

    def update(self, project_id, user_id, data):
        cmd = UpdateProjectCommand(project_id, user_id, data)
        return self.handler.handle_update(cmd)

    def delete(self, project_id, user_id):
        cmd = DeleteProjectCommand(project_id, user_id)
        return self.handler.handle_delete(cmd)

    def add_member(self, project_id, user_id, member_user_id):
        cmd = AddMemberCommand(project_id, user_id, member_user_id)
        return self.handler.handle_add_member(cmd)

    def remove_member(self, project_id, user_id, member_user_id):
        cmd = RemoveMemberCommand(project_id, user_id, member_user_id)
        return self.handler.handle_remove_member(cmd)

    def get_members(self, project_id, user_id):
        project = self.get_by_id(project_id, user_id)
        return project.members.all()

_project_service = None

def get_project_service():
    global _project_service
    if _project_service is None:
        _project_service = ProjectService()
    return _project_service

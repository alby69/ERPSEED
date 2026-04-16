from models import User, Project
from extensions import db
from flask_smorest import abort
from sqlalchemy import text
from core.events.triggers import on_project_created, on_project_updated, on_project_deleted

class ProjectCommandHandler:
    def handle_create(self, cmd):
        existing = Project.query.filter_by(name=cmd.name).first()
        if existing:
            abort(409, message=f"A project with name '{cmd.name}' already exists.")

        owner = db.session.get(User, cmd.owner_id)
        if not owner:
            abort(404, message="Owner user not found.")

        project = Project(
            name=cmd.name,
            title=cmd.title,
            description=cmd.description,
            owner_id=cmd.owner_id
        )

        if owner:
            project.members.append(owner)

        db.session.add(project)
        db.session.flush()

        schema_name = f"project_{project.id}"
        db.session.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
        db.session.commit()

        try:
            on_project_created(project)
        except Exception:
            pass
        return project

    def handle_update(self, cmd):
        project = db.session.get(Project, cmd.project_id)
        if not project:
            abort(404, message="Project not found.")

        user = db.session.get(User, cmd.user_id)
        if user.role != 'admin' and project.owner_id != cmd.user_id:
            abort(403, message="Only the owner or an admin can modify the project.")

        for key, value in cmd.data.items():
            if hasattr(project, key):
                setattr(project, key, value)

        db.session.commit()
        try:
            on_project_updated(project)
        except Exception:
            pass
        return project

    def handle_delete(self, cmd):
        project = db.session.get(Project, cmd.project_id)
        if not project:
            abort(404, message="Project not found.")

        user = db.session.get(User, cmd.user_id)
        if user.role != 'admin' and project.owner_id != cmd.user_id:
            abort(403, message="Only the owner or an admin can delete the project.")

        project_name = project.name
        project_id = project.id
        schema_name = f"project_{project.id}"
        db.session.execute(text(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE'))

        db.session.delete(project)
        db.session.commit()
        try:
            on_project_deleted(project_id, project_name)
        except Exception:
            pass
        return True

    def handle_add_member(self, cmd):
        project = db.session.get(Project, cmd.project_id)
        if not project:
            abort(404, message="Project not found.")

        user = db.session.get(User, cmd.user_id)
        if user.role != 'admin' and project.owner_id != cmd.user_id:
            abort(403, message="Only the owner or an admin can add members.")

        user_to_add = db.session.get(User, cmd.member_user_id)
        if not user_to_add:
            abort(404, message="User to add not found.")

        if user_to_add in project.members:
            abort(409, message=f"User {user_to_add.email} is already a member of this project.")

        project.members.append(user_to_add)
        db.session.commit()
        return user_to_add

    def handle_remove_member(self, cmd):
        project = db.session.get(Project, cmd.project_id)
        if not project:
            abort(404, message="Project not found.")

        user = db.session.get(User, cmd.user_id)
        if user.role != 'admin' and project.owner_id != cmd.user_id:
            abort(403, message="Only the owner or an admin can remove members.")

        user_to_remove = db.session.get(User, cmd.member_user_id)
        if not user_to_remove:
            abort(404, message="User not found.")

        if user_to_remove.id == project.owner_id:
            abort(400, message="Cannot remove the project owner.")

        if user_to_remove not in project.members:
            abort(404, message="User is not a member of this project.")

        project.members.remove(user_to_remove)
        db.session.commit()
        return True

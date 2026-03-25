"""
Project Service - Handles project-related business logic.
"""
from sqlalchemy import text
from flask_smorest import abort

from .base import BaseService


class ProjectService(BaseService):
    """
    Service for managing projects and their related operations.
    Handles multi-tenancy through PostgreSQL schemas.
    """

    def get_all_for_user(self, user_id):
        """
        Get all projects the user has access to.

        Args:
            user_id: The ID of the user making the request.

        Returns:
            Query of projects the user can access.
        """
        from ..models import User, Project

        user = self.db.session.get(User, user_id)
        if not user:
            abort(404, message="User not found.")

        if user.role == 'admin':
            return Project.query.order_by(Project.name)

        return Project.query.filter(
            (Project.owner_id == user_id) | (Project.members.any(id=user_id))
        ).order_by(Project.name)

    def get_by_id(self, project_id, user_id):
        """
        Get a single project by ID with access control.

        Args:
            project_id: ID of the project to retrieve.
            user_id: ID of the user making the request.

        Returns:
            Project instance if accessible.

        Raises:
            403: If user doesn't have access.
            404: If project not found.
        """
        from ..models import User, Project

        project = self.db.session.get(Project, project_id)
        if not project:
            abort(404, message="Project not found.")

        user = self.db.session.get(User, user_id)

        is_member = project.members.filter_by(id=user_id).first() is not None

        if user.role != 'admin' and project.owner_id != user_id and not is_member:
            abort(403, message="You don't have access to this project.")

        return project

    def create(self, name, title, description, owner_id):
        """
        Create a new project with associated schema.

        Args:
            name: Internal name for the project.
            title: Display title.
            description: Optional description.
            owner_id: ID of the user who owns the project.

        Returns:
            Newly created Project instance.

        Raises:
            409: If project name already exists.
        """
        from ..models import User, Project

        existing = Project.query.filter_by(name=name).first()
        if existing:
            abort(409, message=f"A project with name '{name}' already exists.")

        owner = self.db.session.get(User, owner_id)
        if not owner:
            abort(404, message="Owner user not found.")

        project = Project(
            name=name,
            title=title,
            description=description,
            owner_id=owner_id
        )

        if owner:
            project.members.append(owner)

        self.db.session.add(project)
        self.db.session.flush()

        schema_name = f"project_{project.id}"
        self.db.session.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
        self.db.session.commit()

        try:
            from ..webhook_triggers import on_project_created
            on_project_created(project)
        except Exception:
            pass

        return project

    def update(self, project_id, user_id, data):
        """
        Update an existing project.

        Args:
            project_id: ID of the project to update.
            user_id: ID of the user making the request.
            data: Dictionary of fields to update.

        Returns:
            Updated Project instance.

        Raises:
            403: If user is not authorized.
        """
        from ..models import User, Project

        project = self.db.session.get(Project, project_id)
        if not project:
            abort(404, message="Project not found.")

        user = self.db.session.get(User, user_id)

        if user.role != 'admin' and project.owner_id != user_id:
            abort(403, message="Only the owner or an admin can modify the project.")

        for key, value in data.items():
            if hasattr(project, key):
                setattr(project, key, value)

        self.db.session.commit()

        try:
            from ..webhook_triggers import on_project_updated
            on_project_updated(project)
        except Exception:
            pass

        return project

    def delete(self, project_id, user_id):
        """
        Delete a project and its schema.

        Args:
            project_id: ID of the project to delete.
            user_id: ID of the user making the request.

        Raises:
            403: If user is not authorized.
        """
        from ..models import User, Project

        project = self.db.session.get(Project, project_id)
        if not project:
            abort(404, message="Project not found.")

        user = self.db.session.get(User, user_id)

        if user.role != 'admin' and project.owner_id != user_id:
            abort(403, message="Only the owner or an admin can delete the project.")

        project_name = project.name
        project_id = project.id
        schema_name = f"project_{project.id}"
        self.db.session.execute(text(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE'))

        self.db.session.delete(project)
        self.db.session.commit()

        try:
            from ..webhook_triggers import on_project_deleted
            on_project_deleted(project_id, project_name)
        except Exception:
            pass

    def add_member(self, project_id, user_id, member_user_id):
        """
        Add a member to a project.

        Args:
            project_id: ID of the project.
            user_id: ID of the user making the request.
            member_user_id: ID of the user to add.

        Returns:
            The added User member.

        Raises:
            403: If user is not authorized.
            409: If user is already a member.
        """
        from ..models import User, Project

        project = self.db.session.get(Project, project_id)
        if not project:
            abort(404, message="Project not found.")

        user = self.db.session.get(User, user_id)

        if user.role != 'admin' and project.owner_id != user_id:
            abort(403, message="Only the owner or an admin can add members.")

        user_to_add = self.db.session.get(User, member_user_id)
        if not user_to_add:
            abort(404, message="User to add not found.")

        if user_to_add in project.members:
            abort(409, message=f"User {user_to_add.email} is already a member of this project.")

        project.members.append(user_to_add)
        self.db.session.commit()

        return user_to_add

    def remove_member(self, project_id, user_id, member_user_id):
        """
        Remove a member from a project.

        Args:
            project_id: ID of the project.
            user_id: ID of the user making the request.
            member_user_id: ID of the user to remove.

        Raises:
            403: If user is not authorized.
            400: If trying to remove the owner.
            404: If user is not a member.
        """
        from ..models import User, Project

        project = self.db.session.get(Project, project_id)
        if not project:
            abort(404, message="Project not found.")

        user = self.db.session.get(User, user_id)

        if user.role != 'admin' and project.owner_id != user_id:
            abort(403, message="Only the owner or an admin can remove members.")

        user_to_remove = self.db.session.get(User, member_user_id)
        if not user_to_remove:
            abort(404, message="User not found.")

        if user_to_remove.id == project.owner_id:
            abort(400, message="Cannot remove the project owner.")

        if user_to_remove not in project.members:
            abort(404, message="User is not a member of this project.")

        project.members.remove(user_to_remove)
        self.db.session.commit()

    def get_members(self, project_id, user_id):
        """
        Get all members of a project.

        Args:
            project_id: ID of the project.
            user_id: ID of the user making the request.

        Returns:
            List of User members.

        Raises:
            403: If user is not authorized.
        """
        from ..models import User, Project

        project = self.db.session.get(Project, project_id)
        if not project:
            abort(404, message="Project not found.")

        user = self.db.session.get(User, user_id)

        is_member = project.members.filter_by(id=user_id).first() is not None

        if user.role != 'admin' and project.owner_id != user_id and not is_member:
            abort(403, message="You don't have access to this project's members.")

        return project.members.all()

    def export_template(self, project_id):
        """
        Export project as a JSON template.

        Args:
            project_id: ID of the project to export.

        Returns:
            Dictionary containing the template data.
        """
        import json
        from ..models import Project

        project = self.db.session.get(Project, project_id)
        if not project:
            abort(404, message="Project not found.")

        export_data = {
            "template_version": "1.0",
            "name": project.name,
            "title": project.title,
            "description": project.description,
            "version": project.version,
            "models": []
        }

        for model in project.models:
            model_data = {
                "name": model.name,
                "title": model.title,
                "description": model.description,
                "permissions": model.permissions,
                "fields": []
            }
            for field in model.fields:
                field_data = {
                    "name": field.name,
                    "title": field.title,
                    "type": field.type,
                    "required": field.required,
                    "is_unique": field.is_unique,
                    "default_value": field.default_value,
                    "options": field.options,
                    "order": field.order,
                    "formula": field.formula,
                    "summary_expression": field.summary_expression,
                    "validation_regex": field.validation_regex,
                    "validation_message": field.validation_message
                }
                model_data["fields"].append(field_data)
            export_data["models"].append(model_data)

        return export_data

    def import_template(self, template_data, user_id):
        """
        Import a project from a JSON template.

        Args:
            template_data: Dictionary containing template data.
            user_id: ID of the user performing the import.

        Returns:
            Tuple of (message, project_id).
        """
        from ..models import Project, SysModel, SysField

        if template_data.get('template_version') != '1.0':
            abort(400, message="Template version not supported or missing.")

        if 'name' not in template_data:
            abort(400, message="Invalid template: missing project name")

        name = template_data['name']
        project = Project.query.filter_by(name=name).first()
        action = "created"

        if project:
            project.title = template_data.get('title', project.title)
            project.description = template_data.get('description', project.description)
            project.version = template_data.get('version', project.version)
            action = "updated"
        else:
            project = Project(
                name=name,
                title=template_data.get('title', name),
                description=template_data.get('description'),
                version=template_data.get('version', '1.0.0'),
                owner_id=user_id
            )
            self.db.session.add(project)

        self.db.session.flush()

        schema_name = f"project_{project.id}"
        self.db.session.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
        self.db.session.flush()

        processed_model_ids = []

        for m_data in template_data.get('models', []):
            m_name = m_data['name']
            model = SysModel.query.filter_by(project_id=project.id, name=m_name).first()

            if model:
                model.title = m_data.get('title', model.title)
                model.description = m_data.get('description', model.description)
                model.permissions = m_data.get('permissions', model.permissions)
            else:
                model = SysModel(
                    project_id=project.id,
                    name=m_name,
                    title=m_data.get('title', m_data.get('name')),
                    description=m_data.get('description'),
                    permissions=m_data.get('permissions')
                )
                self.db.session.add(model)

            self.db.session.flush()

            processed_model_ids.append(model.id)
            processed_field_ids = []

            for f_data in m_data.get('fields', []):
                f_name = f_data['name']
                field = SysField.query.filter_by(model_id=model.id, name=f_name).first()

                if field:
                    field.title = f_data.get('title', field.title)
                    field.type = f_data.get('type', field.type)
                    field.required = f_data.get('required', field.required)
                    field.is_unique = f_data.get('is_unique', field.is_unique)
                    field.default_value = f_data.get('default_value', field.default_value)
                    field.options = f_data.get('options', field.options)
                    field.order = f_data.get('order', field.order)
                    field.formula = f_data.get('formula', field.formula)
                    field.summary_expression = f_data.get('summary_expression', field.summary_expression)
                    field.validation_regex = f_data.get('validation_regex', field.validation_regex)
                    field.validation_message = f_data.get('validation_message', field.validation_message)
                else:
                    field = SysField(
                        model_id=model.id,
                        name=f_name,
                        title=f_data.get('title'),
                        type=f_data['type'],
                        required=f_data.get('required', False),
                        is_unique=f_data.get('is_unique', False),
                        default_value=f_data.get('default_value'),
                        options=f_data.get('options'),
                        order=f_data.get('order', 0),
                        formula=f_data.get('formula'),
                        summary_expression=f_data.get('summary_expression'),
                        validation_regex=f_data.get('validation_regex'),
                        validation_message=f_data.get('validation_message')
                    )
                    self.db.session.add(field)

                self.db.session.flush()
                processed_field_ids.append(field.id)

            if processed_field_ids:
                SysField.query.filter(
                    SysField.model_id == model.id,
                    SysField.id.notin_(processed_field_ids)
                ).delete(synchronize_session=False)
            else:
                SysField.query.filter(SysField.model_id == model.id).delete(synchronize_session=False)

        if processed_model_ids:
            SysModel.query.filter(
                SysModel.project_id == project.id,
                SysModel.id.notin_(processed_model_ids)
            ).delete(synchronize_session=False)
        else:
            SysModel.query.filter(SysModel.project_id == project.id).delete(synchronize_session=False)

        self.db.session.commit()

        return f"Project '{project.title}' {action} successfully.", project.id

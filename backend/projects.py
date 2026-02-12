from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from flask import make_response, request
from sqlalchemy import text

from .models import Project, SysModel, SysField, User
from .extensions import db
from .schemas import ProjectSchema, ProjectUpdateSchema, SysModelSchema, SysModelCreateSchema, ProjectMemberSchema, UserDisplaySchema
from .decorators import admin_required
from .utils import paginate

blp = Blueprint("projects", "projects", url_prefix="/projects", description="Operations on projects")

@blp.route("")
class ProjectList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, ProjectSchema(many=True))
    def get(self):
        """Elenca i progetti a cui l'utente ha accesso"""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if user.role == 'admin':
            # L'admin vede tutti i progetti
            query = Project.query.order_by(Project.name)
        else:
            # Gli altri utenti vedono solo i progetti di cui sono proprietari o membri
            query = Project.query.filter(
                (Project.owner_id == user_id) | (Project.members.any(id=user_id))
            ).order_by(Project.name)

        items, headers = paginate(query)
        return items, 200, headers

    @blp.doc(security=[{"jwt": []}])
    @admin_required()
    @blp.arguments(ProjectSchema)
    @blp.response(201, ProjectSchema)
    def post(self, project_data):
        """Crea un nuovo progetto (solo Admin)"""
        if Project.query.filter_by(name=project_data.name).first():
            abort(409, message=f"Un progetto con nome '{project_data.name}' esiste già.")
        
        owner_id = get_jwt_identity()
        owner = User.query.get(owner_id)

        # Imposta il proprietario sull'utente admin corrente
        project_data.owner_id = owner_id
        
        # Aggiungi il proprietario come primo membro del progetto
        if owner:
            project_data.members.append(owner)

        db.session.add(project_data)
        db.session.commit()
        
        # Crea lo schema PostgreSQL per il progetto
        schema_name = f"project_{project_data.id}"
        db.session.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
        db.session.commit()
        
        return project_data

@blp.route("/<int:project_id>")
class ProjectResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, ProjectSchema)
    def get(self, project_id):
        """Ottiene i dettagli di un progetto per ID"""
        project = Project.query.get_or_404(project_id)
        
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        # Admin, Owner e Membri possono vedere i dettagli
        is_member = project.members.filter_by(id=current_user_id).first() is not None
        
        if current_user.role != 'admin' and project.owner_id != current_user_id and not is_member:
             abort(403, message="Non hai accesso a questo progetto.")
        
        return project

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(ProjectUpdateSchema)
    @blp.response(200, ProjectSchema)
    def put(self, update_data, project_id):
        """Aggiorna un progetto esistente (Admin o Owner)"""
        project = Project.query.get_or_404(project_id)

        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)

        if current_user.role != 'admin' and project.owner_id != current_user_id:
             abort(403, message="Solo il proprietario o un admin possono modificare il progetto.")

        for key, value in update_data.items():
            setattr(project, key, value)
        
        db.session.commit()
        return project

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, project_id):
        """Elimina un progetto (Admin o Owner)"""
        project = Project.query.get_or_404(project_id)

        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)

        if current_user.role != 'admin' and project.owner_id != current_user_id:
             abort(403, message="Solo il proprietario o un admin possono eliminare il progetto.")

        # Drop the project-specific schema from the database
        schema_name = f"project_{project.id}"
        db.session.execute(text(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE'))

        db.session.delete(project)
        db.session.commit()
        return ""

@blp.route("/<int:project_id>/models")
class ProjectModels(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, SysModelSchema(many=True))
    def get(self, project_id):
        """Lista tutti i modelli di un progetto"""
        project = Project.query.get_or_404(project_id)
        return project.models

    @blp.doc(security=[{"jwt": []}])
    @admin_required()
    @blp.arguments(SysModelCreateSchema)
    @blp.response(201, SysModelSchema)
    def post(self, model_data, project_id):
        """Crea un nuovo modello in un progetto (solo Admin)"""
        Project.query.get_or_404(project_id)

        if SysModel.query.filter_by(project_id=project_id, name=model_data.name).first():
            abort(409, message=f"Un modello con nome '{model_data.name}' esiste già in questo progetto.")
        
        model_data.project_id = project_id
        db.session.add(model_data)
        db.session.commit()
        return model_data

@blp.route("/<int:project_id>/members")
class ProjectMemberList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, UserDisplaySchema(many=True))
    def get(self, project_id):
        """Elenca i membri di un progetto"""
        project = Project.query.get_or_404(project_id)
        
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        # Admin, Owner e Membri possono vedere la lista
        is_member = project.members.filter_by(id=current_user_id).first() is not None
        
        if current_user.role != 'admin' and project.owner_id != current_user_id and not is_member:
             abort(403, message="Non hai accesso ai membri di questo progetto.")

        return project.members.all()

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(ProjectMemberSchema)
    @blp.response(201, UserDisplaySchema)
    def post(self, member_data, project_id):
        """Aggiunge un membro a un progetto (Admin o Owner)"""
        project = Project.query.get_or_404(project_id)
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)

        if current_user.role != 'admin' and project.owner_id != current_user_id:
             abort(403, message="Solo il proprietario o un admin possono aggiungere membri.")

        user_to_add = User.query.get_or_404(member_data['user_id'])

        if user_to_add in project.members:
            abort(409, message=f"L'utente {user_to_add.email} è già membro di questo progetto.")

        project.members.append(user_to_add)
        db.session.commit()
        return user_to_add

@blp.route("/<int:project_id>/members/<int:user_id>")
class ProjectMemberResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, project_id, user_id):
        """Rimuove un membro da un progetto (Admin o Owner)"""
        project = Project.query.get_or_404(project_id)
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)

        if current_user.role != 'admin' and project.owner_id != current_user_id:
             abort(403, message="Solo il proprietario o un admin possono rimuovere membri.")

        user_to_remove = User.query.get_or_404(user_id)

        if user_to_remove.id == project.owner_id:
            abort(400, message="Non è possibile rimuovere il proprietario del progetto.")

        if user_to_remove not in project.members:
            abort(404, message="L'utente non è membro di questo progetto.")

        project.members.remove(user_to_remove)
        db.session.commit()
        return ""

@blp.route("/<int:project_id>/export")
class ProjectExport(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @admin_required()
    def get(self, project_id):
        """Esporta il progetto come template JSON"""
        project = Project.query.get_or_404(project_id)
        
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
            
        response = make_response(json.dumps(export_data, indent=2))
        response.headers["Content-Disposition"] = f"attachment; filename={project.name}_template.json"
        response.headers["Content-Type"] = "application/json"
        return response

@blp.route("/import")
class ProjectImport(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @admin_required()
    def post(self):
        """Importa un progetto da un template JSON (Crea o Aggiorna)"""
        if 'file' not in request.files:
            abort(400, message="No file part")
        
        file = request.files['file']
        if file.filename == '':
            abort(400, message="No selected file")
            
        try:
            data = json.load(file)
        except Exception as e:
            abort(400, message=f"Invalid JSON: {str(e)}")
            
        # Controllo versione template per compatibilità
        if data.get('template_version') != '1.0':
            abort(400, message="Versione template non supportata o mancante.")

        if 'name' not in data:
            abort(400, message="Invalid template: missing project name")
            
        name = data['name']
        project = Project.query.filter_by(name=name).first()
        action = "created"

        if project:
            # Update existing project
            project.title = data.get('title', project.title)
            project.description = data.get('description', project.description)
            project.version = data.get('version', project.version)
            action = "updated"
        else:
            # Create new project
            project = Project(
                name=name,
                title=data.get('title', name),
                description=data.get('description'),
                version=data.get('version', '1.0.0'),
                owner_id=get_jwt_identity()
            )
            db.session.add(project)
        
        db.session.flush()
        
        # Crea lo schema PostgreSQL per il progetto
        schema_name = f"project_{project.id}"
        db.session.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
        db.session.flush()
        
        processed_model_ids = []
        
        for m_data in data.get('models', []):
            m_name = m_data['name']
            model = SysModel.query.filter_by(project_id=project.id, name=m_name).first()

            if model:
                # Update existing model
                model.title = m_data.get('title', model.title)
                model.description = m_data.get('description', model.description)
                model.permissions = m_data.get('permissions', model.permissions)
            else:
                # Create new model
                model = SysModel(
                    project_id=project.id,
                    name=m_name,
                    title=m_data.get('title', m_data.get('name')),
                    description=m_data.get('description'),
                    permissions=m_data.get('permissions')
                )
                db.session.add(model)
            
            db.session.flush()
            
            processed_model_ids.append(model.id)
            processed_field_ids = []
            
            for f_data in m_data.get('fields', []):
                f_name = f_data['name']
                field = SysField.query.filter_by(model_id=model.id, name=f_name).first()
                
                if field:
                    # Update field
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
                    # Create field
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
                    db.session.add(field)
                
                db.session.flush()
                processed_field_ids.append(field.id)
            
            # Delete fields not present in the import
            if processed_field_ids:
                SysField.query.filter(
                    SysField.model_id == model.id,
                    SysField.id.notin_(processed_field_ids)
                ).delete(synchronize_session=False)
            else:
                SysField.query.filter(SysField.model_id == model.id).delete(synchronize_session=False)
                
        # Delete models not present in the import
        if processed_model_ids:
            SysModel.query.filter(
                SysModel.project_id == project.id,
                SysModel.id.notin_(processed_model_ids)
            ).delete(synchronize_session=False)
        else:
            SysModel.query.filter(SysModel.project_id == project.id).delete(synchronize_session=False)

        db.session.commit()
        
        return {"message": f"Project '{project.title}' {action} successfully.", "project_id": project.id}, 200
from marshmallow import fields
from .extensions import ma
from .models import User, Project, SysModel, SysField, AuditLog

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        # Nasconde l'hash della password dalla serializzazione
        exclude = ("password_hash",)
        # Rende la password obbligatoria solo in fase di creazione/caricamento
        load_only = ("password",)
    
    # Campo password per il caricamento (non viene mai mostrato in output)
    password = fields.Str(required=True, load_only=True)

class UserUpdateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        exclude = ("password_hash",)
        # Tutti i campi sono opzionali per gli aggiornamenti
        partial = True

class AdminPasswordResetSchema(ma.Schema):
    new_password = fields.Str(required=True)

# --- Schemi per i Progetti ---
class ProjectSchema(ma.SQLAlchemyAutoSchema):
    # Mostra i dettagli del proprietario in sola lettura
    owner = fields.Nested(UserSchema(only=("id", "email")), dump_only=True)
    
    class Meta:
        model = Project
        load_instance = True
        include_fk = True
        # Campi gestiti automaticamente dal server
        dump_only = ("id", "created_at", "updated_at", "owner")

class ProjectUpdateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Project
        load_instance = True
        partial = True
        # Non permettere di cambiare il proprietario tramite API
        exclude = ("owner_id",)

# --- Schemi per il Builder ---
class SysFieldSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SysField
        load_instance = True
        include_fk = True

class SysModelSchema(ma.SQLAlchemyAutoSchema):
    fields = fields.List(fields.Nested(SysFieldSchema))
    project = fields.Nested(ProjectSchema(only=("id", "name")))
    
    class Meta:
        model = SysModel
        load_instance = True
        include_fk = True

class SysModelCreateSchema(ma.SQLAlchemyAutoSchema):
    fields = fields.List(fields.Nested(SysFieldSchema))
    
    class Meta:
        model = SysModel
        load_instance = True
        include_fk = True
        exclude = ("project_id", "project")

class AuditLogSchema(ma.SQLAlchemyAutoSchema):
    user = fields.Nested(UserSchema(only=("id", "email")))
    class Meta:
        model = AuditLog
        load_instance = True
        include_fk = True
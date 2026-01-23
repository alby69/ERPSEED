from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

class BaseModel(db.Model):
    """Modello base con campi comuni per tutti gli altri modelli."""
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Project(BaseModel):
    """
    Rappresenta un Progetto o un'istanza applicativa creata con il Builder.
    Ogni progetto è un contenitore per un insieme di modelli (SysModel).
    """
    __tablename__ = 'projects'
    name = db.Column(db.String(80), unique=True, nullable=False, help_text="Nome interno del progetto (es. 'fleet_management')")
    title = db.Column(db.String(120), nullable=False, help_text="Titolo visualizzato per il progetto")
    description = db.Column(db.Text)
    version = db.Column(db.String(20), default="1.0.0", help_text="Versione del progetto")
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relazioni
    models = db.relationship('SysModel', back_populates='project', lazy='dynamic', cascade="all, delete-orphan")
    owner = db.relationship('User')

    def __repr__(self):
        return f'<Project {self.name}>'

class User(BaseModel):
    """Modello per gli utenti del sistema."""
    __tablename__ = 'users'
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    role = db.Column(db.String(80), default='user', nullable=False, help_text="Ruolo dell'utente (es. admin, user)")
    is_active = db.Column(db.Boolean, default=True)
    force_password_change = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

class SysModel(BaseModel):
    """Definizione di un modello (tabella) creato dinamicamente dal Builder."""
    __tablename__ = 'sys_models'
    name = db.Column(db.String(80), unique=True, nullable=False)
    title = db.Column(db.String(120))
    description = db.Column(db.Text)
    permissions = db.Column(db.Text, help_text="JSON string for Access Control List (ACL)")
    
    # Ogni modello DEVE appartenere a un progetto
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    
    # Relazioni
    fields = db.relationship('SysField', back_populates='model', lazy='joined', cascade="all, delete-orphan", order_by='SysField.order')
    project = db.relationship('Project', back_populates='models')

    def __repr__(self):
        return f'<SysModel {self.name}>'

class SysField(BaseModel):
    """Definizione di un campo (colonna) per un SysModel."""
    __tablename__ = 'sys_fields'
    name = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(120))
    type = db.Column(db.String(50), nullable=False)
    required = db.Column(db.Boolean, default=False)
    is_unique = db.Column(db.Boolean, default=False)
    default_value = db.Column(db.String(255))
    options = db.Column(db.Text, help_text="JSON for select options, relation config, etc.")
    order = db.Column(db.Integer, default=0)
    formula = db.Column(db.String(255))
    summary_expression = db.Column(db.String(255))
    validation_regex = db.Column(db.String(255))
    validation_message = db.Column(db.String(255))
    
    model_id = db.Column(db.Integer, db.ForeignKey('sys_models.id'), nullable=False)
    
    # Relazioni
    model = db.relationship('SysModel', back_populates='fields')

    def __repr__(self):
        return f'<SysField {self.name} in {self.model.name}>'

class AuditLog(BaseModel):
    """Log delle azioni significative eseguite nel sistema."""
    __tablename__ = 'audit_logs'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    model_name = db.Column(db.String(80))
    record_id = db.Column(db.Integer)
    action = db.Column(db.String(50), help_text="CREATE, UPDATE, DELETE, LOGIN, etc.")
    changes = db.Column(db.Text, help_text="JSON diff of the changes")
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, index=True)
    
    # Relazioni
    user = db.relationship('User')
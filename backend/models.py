from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

class BaseModel(db.Model):
    """Base model with common fields for all other models."""
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

project_members = db.Table('project_members',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True)
)

class Project(BaseModel):
    """
    Represents a Project or application instance created with the Builder.
    Each project is a container for a set of models (SysModel).
    """
    __tablename__ = 'projects'
    name = db.Column(db.String(80), unique=True, nullable=False, comment="Internal project name (e.g., 'fleet_management')")
    title = db.Column(db.String(120), nullable=False, comment="Display title for the project")
    description = db.Column(db.Text)
    version = db.Column(db.String(20), default="1.0.0", comment="Project version")
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    models = db.relationship('SysModel', back_populates='project', lazy='dynamic', cascade="all, delete-orphan")
    owner = db.relationship('User')
    members = db.relationship('User', secondary=project_members, back_populates='projects', lazy='dynamic')

    def __repr__(self):
        return f'<Project {self.name}>'

class User(BaseModel):
    """User model for system users."""
    __tablename__ = 'users'
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    role = db.Column(db.String(80), default='user', nullable=False, comment="User role (e.g., admin, user)")
    is_active = db.Column(db.Boolean, default=True)
    force_password_change = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.String(255), nullable=True)

    projects = db.relationship('Project', secondary=project_members, back_populates='members', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

class SysModel(BaseModel):
    """Definition of a model (table) created dynamically by the Builder."""
    __tablename__ = 'sys_models'
    name = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(120))
    description = db.Column(db.Text)
    permissions = db.Column(db.Text, comment="JSON string for Access Control List (ACL)")
    
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    
    __table_args__ = (db.UniqueConstraint('project_id', 'name', name='_project_model_name_uc'),)

    fields = db.relationship('SysField', back_populates='model', lazy='joined', cascade="all, delete-orphan", order_by='SysField.order')
    project = db.relationship('Project', back_populates='models')

    def __repr__(self):
        return f'<SysModel {self.name}>'

class SysField(BaseModel):
    """Definition of a field (column) for a SysModel."""
    __tablename__ = 'sys_fields'
    name = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(120))
    type = db.Column(db.String(50), nullable=False)
    required = db.Column(db.Boolean, default=False)
    is_unique = db.Column(db.Boolean, default=False)
    default_value = db.Column(db.String(255))
    options = db.Column(db.Text, comment="JSON for select options, relation config, etc.")
    order = db.Column(db.Integer, default=0)
    formula = db.Column(db.String(255))
    summary_expression = db.Column(db.String(255))
    validation_regex = db.Column(db.String(255))
    validation_message = db.Column(db.String(255))
    
    model_id = db.Column(db.Integer, db.ForeignKey('sys_models.id'), nullable=False)
    
    model = db.relationship('SysModel', back_populates='fields')

    def __repr__(self):
        return f'<SysField {self.name} in {self.model.name}>'

class AuditLog(BaseModel):
    """Log of significant actions performed in the system."""
    __tablename__ = 'audit_logs'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    model_name = db.Column(db.String(80))
    record_id = db.Column(db.Integer)
    action = db.Column(db.String(50), comment="CREATE, UPDATE, DELETE, LOGIN, etc.")
    changes = db.Column(db.Text, comment="JSON diff of the changes")
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, index=True)
    
    user = db.relationship('User')

class Party(BaseModel):
    """Generic master data for customers, suppliers, etc."""
    __tablename__ = 'parties'
    
    name = db.Column(db.String(150), nullable=False, index=True)
    party_type = db.Column(db.String(50), nullable=False, default='Customer', comment="E.g., Customer, Supplier")
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(50))
    vat_number = db.Column(db.String(50), unique=True, index=True)
    fiscal_code = db.Column(db.String(50), unique=True)

    def __repr__(self):
        return f'<Party {self.name}>'

class Product(BaseModel):
    """Product/Service master data."""
    __tablename__ = 'products'
    
    name = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(50), unique=True, index=True)
    description = db.Column(db.Text)
    unit_price = db.Column(db.Float)
    
    def __repr__(self):
        return f'<Product {self.name}>'

class SalesOrder(BaseModel):
    __tablename__ = 'sales_orders'
    
    number = db.Column(db.String(50), unique=True, nullable=False)
    date = db.Column(db.Date, default=datetime.date.today)
    customer_id = db.Column(db.Integer, db.ForeignKey('parties.id'), nullable=False)
    
    customer = db.relationship('Party')
    lines = db.relationship('SalesOrderLine', back_populates='order', cascade="all, delete-orphan")

class SalesOrderLine(BaseModel):
    __tablename__ = 'sales_order_lines'
    
    order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    description = db.Column(db.String(255))
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    
    order = db.relationship('SalesOrder', back_populates='lines')
    product = db.relationship('Product')

class SysChart(BaseModel):
    __tablename__ = 'sys_charts'
    title = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(50), nullable=False) # bar, line, pie, table
    model_id = db.Column(db.Integer, db.ForeignKey('sys_models.id'), nullable=False)
    x_axis = db.Column(db.String(80))
    y_axis = db.Column(db.String(80))
    aggregation = db.Column(db.String(20)) # sum, avg, count
    filters = db.Column(db.Text) # JSON
    
    model = db.relationship('SysModel')

class SysDashboard(BaseModel):
    __tablename__ = 'sys_dashboards'
    title = db.Column(db.String(120), nullable=False)
    configuration = db.Column(db.Text) # JSON layout

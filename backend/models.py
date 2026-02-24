from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

# Import core models to register them with SQLAlchemy
try:
    from backend.core.models import Tenant, TenantMember
except ImportError:
    pass

# Import entities - Soggetto is the main subject entity
try:
    from backend.entities.soggetto import Soggetto
except ImportError:
    pass

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
    
    # Theme Settings
    primary_color = db.Column(db.String(20), default="#1677ff")
    border_radius = db.Column(db.Integer, default=6)
    theme_mode = db.Column(db.String(20), default="light") # light, dark

    models = db.relationship('SysModel', back_populates='project', lazy='dynamic', cascade="all, delete-orphan")
    owner = db.relationship('User')
    members = db.relationship('User', secondary=project_members, back_populates='projects', lazy='dynamic')

    def __repr__(self):
        return f'<Project {self.name}>'

class User(BaseModel):
    """User model for system users."""
    __tablename__ = 'users'
    
    # Tenant (required - will be added via migration)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True, index=True)
    
    # Credentials
    email = db.Column(db.String(120), nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    role = db.Column(db.String(80), default='user', nullable=False, comment="User role (e.g., admin, user)")
    is_active = db.Column(db.Boolean, default=True)
    force_password_change = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.String(255), nullable=True)
    
    # Multi-tenant fields
    is_primary = db.Column(db.Boolean, default=False, comment="Primary admin of tenant")
    last_login_at = db.Column(db.DateTime)
    login_count = db.Column(db.Integer, default=0)
    password_reset_token = db.Column(db.String(255))
    password_reset_expires = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)
    
    # Relationships
    tenant = db.relationship('Tenant', backref=db.backref('tenant_users', lazy='dynamic'))
    projects = db.relationship('Project', secondary=project_members, back_populates='members', lazy='dynamic')
    tenant_members = db.relationship('TenantMember', back_populates='user', foreign_keys='TenantMember.user_id', lazy='dynamic')
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'email', name='uix_tenant_email'),
    )
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    @property
    def full_name(self):
        full = f"{self.first_name or ''} {self.last_name or ''}".strip()
        return full or self.email
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        self.force_password_change = False
        self.password_reset_token = None
        self.password_reset_expires = None

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def record_login(self):
        """Record user login."""
        self.last_login_at = datetime.datetime.utcnow()
        self.login_count += 1
    
    def to_dict(self, include_email=True):
        """Serialize user."""
        result = {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'is_primary': self.is_primary,
            'tenant_id': self.tenant_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if not include_email:
            result.pop('email', None)
        return result

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

# NOTE: AuditLog moved to backend/core/models/audit.py
# Keeping old class for compatibility during migration

# class AuditLog(BaseModel):
#     """Log of significant actions performed in the system."""
#     __tablename__ = 'audit_logs'
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#     model_name = db.Column(db.String(80))
#     record_id = db.Column(db.Integer)
#     action = db.Column(db.String(50), comment="CREATE, UPDATE, DELETE, LOGIN, etc.")
#     changes = db.Column(db.Text, comment="JSON diff of the changes")
#     timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, index=True)
#     
#     user = db.relationship('User')

# NOTE: Party model was replaced by Soggetto in backend/entities/soggetto.py
# Use Soggetto directly or import from backend.entities.soggetto

class Product(BaseModel):
    """Product/Service master data."""
    __tablename__ = 'products'
    
    # Multi-tenant support
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    
    name = db.Column(db.String(150), nullable=False, index=True)
    code = db.Column(db.String(50), index=True)
    description = db.Column(db.Text)
    unit_price = db.Column(db.Float)
    category = db.Column(db.String(100))
    sku = db.Column(db.String(50))
    barcode = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    track_inventory = db.Column(db.Boolean, default=False)
    current_stock = db.Column(db.Float, default=0)
    reorder_level = db.Column(db.Float, default=0)
    unit_of_measure = db.Column(db.String(20), default='pcs')
    weight = db.Column(db.Float)
    dimensions = db.Column(db.String(50))
    
    # Relationships
    tenant = db.relationship('Tenant', backref=db.backref('products', lazy='dynamic'))
    
    # Constraints
    __table_args__ = (
        db.Index('ix_product_tenant_code', 'tenant_id', 'code'),
    )
    
    def __repr__(self):
        return f'<Product {self.name}>'

class SalesOrder(BaseModel):
    __tablename__ = 'sales_orders'
    
    # Multi-tenant support
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    
    number = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, default=datetime.date.today)
    customer_id = db.Column(db.Integer, db.ForeignKey('soggetti.id'), nullable=False)
    status = db.Column(db.String(20), default='draft')
    total_amount = db.Column(db.Float, default=0)
    notes = db.Column(db.Text)
    
    # Relationships
    tenant = db.relationship('Tenant', backref=db.backref('sales_orders', lazy='dynamic'))
    customer = db.relationship('Soggetto')
    lines = db.relationship('SalesOrderLine', back_populates='order', cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        db.Index('ix_order_tenant_number', 'tenant_id', 'number'),
    )

class SalesOrderLine(BaseModel):
    __tablename__ = 'sales_order_lines'
    
    # Multi-tenant support
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    
    order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    description = db.Column(db.String(255))
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    
    # Relationships
    tenant = db.relationship('Tenant')
    order = db.relationship('SalesOrder', back_populates='lines')
    product = db.relationship('Product')


class PurchaseOrder(BaseModel):
    __tablename__ = 'purchase_orders'
    
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    
    number = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, default=datetime.date.today)
    supplier_id = db.Column(db.Integer, db.ForeignKey('soggetti.id'), nullable=False)
    status = db.Column(db.String(20), default='draft')
    total_amount = db.Column(db.Float, default=0)
    expected_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    
    tenant = db.relationship('Tenant', backref=db.backref('purchase_orders', lazy='dynamic'))
    supplier = db.relationship('Soggetto')
    lines = db.relationship('PurchaseOrderLine', back_populates='order', cascade="all, delete-orphan")
    
    __table_args__ = (
        db.Index('ix_purchase_tenant_number', 'tenant_id', 'number'),
    )


class PurchaseOrderLine(BaseModel):
    __tablename__ = 'purchase_order_lines'
    
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    
    order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    description = db.Column(db.String(255))
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    quantity_received = db.Column(db.Float, default=0)
    
    tenant = db.relationship('Tenant')
    order = db.relationship('PurchaseOrder', back_populates='lines')
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

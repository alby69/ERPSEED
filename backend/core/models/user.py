"""
User model with multi-tenant support.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from backend.core.models.base import BaseModel
from backend.extensions import db


class User(BaseModel):
    """
    User model - each user belongs to a tenant.
    """
    __tablename__ = 'users'
    
    # Tenant (required for all users)
    tenant_id = db.Column(
        db.Integer, 
        db.ForeignKey('tenants.id'), 
        nullable=False,
        index=True
    )
    
    # Credentials
    email = db.Column(db.String(120), nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Profile
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    avatar = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    
    # Role in tenant
    role = db.Column(
        db.String(50), 
        nullable=False, 
        default='user'
    )  # admin, manager, user, viewer
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_primary = db.Column(db.Boolean, default=False, comment="Primary admin of tenant")
    force_password_change = db.Column(db.Boolean, default=False)
    
    # Login tracking
    last_login_at = db.Column(db.DateTime)
    login_count = db.Column(db.Integer, default=0)
    
    # Password reset
    password_reset_token = db.Column(db.String(255))
    password_reset_expires = db.Column(db.DateTime)
    
    # Relations
    tenant = db.relationship('Tenant', back_populates='users')
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'email', name='uix_tenant_email'),
        db.Index('ix_user_email_lower', db.func.lower(email)),
    )
    
    def __repr__(self):
        return f'<User {self.email}@{self.tenant.slug if self.tenant else "no-tenant"}>'
    
    @property
    def full_name(self):
        full = f"{self.first_name or ''} {self.last_name or ''}".strip()
        return full or self.email
    
    def set_password(self, password):
        """Set password with hash."""
        self.password_hash = generate_password_hash(password)
        self.force_password_change = False
        self.password_reset_token = None
        self.password_reset_expires = None
    
    def check_password(self, password):
        """Verify password."""
        return check_password_hash(self.password_hash, password)
    
    def record_login(self):
        """Record user login."""
        self.last_login_at = datetime.utcnow()
        self.login_count += 1
    
    def to_dict(self, include_email=True):
        """Serialize user."""
        data = super().to_dict()
        data['full_name'] = self.full_name
        if not include_email:
            data.pop('email', None)
        data.pop('password_hash', None)
        data.pop('password_reset_token', None)
        data.pop('password_reset_expires', None)
        return data


class UserRole(BaseModel):
    """
    Custom roles for tenant with specific permissions.
    """
    __tablename__ = 'user_roles'
    
    tenant_id = db.Column(
        db.Integer, 
        db.ForeignKey('tenants.id'), 
        nullable=False,
        index=True
    )
    
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))
    permissions = db.Column(db.Text, comment="JSON array of permissions")
    is_default = db.Column(db.Boolean, default=False)
    
    tenant = db.relationship('Tenant')
    users = db.relationship('User', backref='custom_role', lazy='dynamic')
    
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'name', name='uix_tenant_role_name'),
    )


# Add custom role foreign key to User
User.custom_role_id = db.Column(db.Integer, db.ForeignKey('user_roles.id'))
User.custom_role = db.relationship('UserRole', backref=db.backref('users', lazy='dynamic'))

"""
Tenant model - represents a company/customer in the system.
Each tenant has isolated data and configuration.
"""
from datetime import datetime
from backend.core.models.base import BaseModel
from backend.extensions import db


class Tenant(BaseModel):
    """
    Tenant - Business entity using the system.
    Each tenant has:
    - Isolated users
    - Isolated data
    - Custom configuration
    """
    __tablename__ = 'tenants'
    
    # Identification
    name = db.Column(db.String(150), nullable=False, index=True)
    slug = db.Column(db.String(80), unique=True, nullable=False, index=True)
    
    # Contact
    email = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    website = db.Column(db.String(255))
    
    # Address
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(2), default='IT')
    
    # Configuration
    timezone = db.Column(db.String(50), default='Europe/Rome')
    locale = db.Column(db.String(5), default='it_IT')
    currency = db.Column(db.String(3), default='EUR')
    
    # Subscription
    plan = db.Column(db.String(50), default='starter')
    plan_expires_at = db.Column(db.DateTime)
    max_users = db.Column(db.Integer, default=3)
    max_storage_mb = db.Column(db.Integer, default=1024)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Branding
    logo = db.Column(db.String(255))
    primary_color = db.Column(db.String(7), default='#3498db')
    
    # Relations
    users = db.relationship('User', back_populates='tenant', lazy='dynamic', overlaps="tenant_users")
    
    def __repr__(self):
        return f'<Tenant {self.slug}>'
    
    @property
    def is_plan_expired(self):
        if self.plan_expires_at is None:
            return False
        return datetime.utcnow() > self.plan_expires_at
    
    def can_add_user(self):
        """Check if more users can be added."""
        return self.users.count() < self.max_users
    
    def can_use_storage(self, bytes_used):
        """Check if storage is available."""
        max_bytes = self.max_storage_mb * 1024 * 1024
        return bytes_used < max_bytes
    
    def to_dict(self, include_config=False):
        """Serialize tenant."""
        data = super().to_dict()
        data.pop('deleted_at', None)
        if not include_config:
            data.pop('plan', None)
            data.pop('plan_expires_at', None)
            data.pop('max_users', None)
            data.pop('max_storage_mb', None)
        return data

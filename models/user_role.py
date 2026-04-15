from extensions import db
from .base import BaseModel


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

    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'name', name='uix_tenant_role_name'),
    )

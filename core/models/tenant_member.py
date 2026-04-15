"""
TenantMember - association between User and Tenant.
"""
from datetime import datetime
from core.models.base import BaseModel
from extensions import db


class TenantMember(BaseModel):
    """
    Association between User and Tenant.
    Defines user's role within a specific tenant.
    """
    __tablename__ = 'tenant_members'

    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey('tenants.id'),
        nullable=False,
        index=True
    )

    userId = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
        index=True
    )

    # Role within this tenant
    ruolo = db.Column(
        db.String(50),
        nullable=False,
        default='user',
        comment="Role in tenant: admin, user"
    )

    # Status
    stato = db.Column(db.String(20), default='attivo',
                      comment="Status: attivo, sospeso")

    # Invitation
    invited_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    invited_at = db.Column(db.DateTime)
    accepted_at = db.Column(db.DateTime)

    # Relations
    tenant = db.relationship('Tenant', back_populates='members')
    user = db.relationship('User', back_populates='tenant_members', foreign_keys=[userId])
    invited_by = db.relationship('User', foreign_keys=[invited_by_id])

    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'userId', name='uix_tenant_user'),
    )

    def __repr__(self):
        return f'<TenantMember user={self.userId} tenant={self.tenant_id} role={self.ruolo}>'

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'userId': self.userId,
            'ruolo': self.ruolo,
            'stato': self.stato,
            'user': self.user.to_dict() if self.user else None,
            'invited_by_id': self.invited_by_id,
            'invited_at': self.invited_at.isoformat() if self.invited_at else None,
            'accepted_at': self.accepted_at.isoformat() if self.accepted_at else None,
        }

"""
Tenant Module - Modulo attivo per un tenant.
"""
from datetime import datetime
from backend.core.models.base import BaseModel
from backend.extensions import db


class TenantModule(BaseModel):
    """
    Modulo attivo per un tenant.
    Tiene traccia di quale modulo è attivo per quale tenant.
    """
    __tablename__ = 'tenant_modules'
    
    tenant_id = db.Column(
        db.Integer, 
        db.ForeignKey('tenants.id'), 
        nullable=False,
        index=True
    )
    
    module_id = db.Column(
        db.String(50), 
        nullable=False,
        index=True
    )
    
    is_enabled = db.Column(db.Boolean, default=False)
    enabled_at = db.Column(db.DateTime)
    disabled_at = db.Column(db.DateTime)
    
    # Licensing
    license_key = db.Column(db.String(255))
    expires_at = db.Column(db.DateTime)
    
    # Configurazione specifica del tenant
    config = db.Column(db.JSON, default=dict)
    
    # Relationships
    tenant = db.relationship('Tenant', backref=db.backref('modules', lazy='dynamic'))
    
    @property
    def module(self):
        """Get module definition (lazy load)."""
        from backend.core.models.module_definition import ModuleDefinition
        return ModuleDefinition.query.filter_by(module_id=self.module_id).first()
    
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'module_id', name='uix_tenant_module'),
    )
    
    def __repr__(self):
        return f'<TenantModule tenant={self.tenant_id} module={self.module_id}>'
    
    def to_dict(self):
        """Serialize tenant module."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'module_id': self.module_id,
            'is_enabled': self.is_enabled,
            'enabled_at': self.enabled_at.isoformat() if self.enabled_at else None,
            'disabled_at': self.disabled_at.isoformat() if self.disabled_at else None,
            'license_key': self.license_key,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'config': self.config or {}
        }

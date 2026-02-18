"""
Audit Log model - tracks all operations in the system.
"""
import json
from datetime import datetime
from backend.core.models.base import BaseModel
from backend.extensions import db


class AuditLog(BaseModel):
    """
    AuditLog - Log of all operations in the system.
    Essential for:
    - Security
    - GDPR compliance
    - Debugging
    - Analytics
    """
    __tablename__ = 'audit_logs'
    
    tenant_id = db.Column(
        db.Integer, 
        db.ForeignKey('tenants.id'), 
        nullable=False,
        index=True
    )
    
    # Who performed the action
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Action details
    action = db.Column(
        db.String(50), 
        nullable=False,
        index=True
    )  # create, update, delete, login, logout, etc.
    resource_type = db.Column(db.String(50), nullable=False, index=True)
    resource_id = db.Column(db.Integer, nullable=True)
    
    # Data changed
    changes = db.Column(db.Text, comment="JSON with changes")
    old_values = db.Column(db.Text)
    new_values = db.Column(db.Text)
    
    # Context
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    endpoint = db.Column(db.String(255))
    method = db.Column(db.String(10))
    
    # Result
    status = db.Column(db.String(20), default='success')  # success, failure
    error_message = db.Column(db.Text)
    
    # Relations
    tenant = db.relationship('Tenant')
    user = db.relationship('User')
    
    # Indexes
    __table_args__ = (
        db.Index('ix_audit_tenant_created', 'tenant_id', 'created_at'),
        db.Index('ix_audit_user_created', 'user_id', 'created_at'),
        db.Index('ix_audit_resource', 'resource_type', 'resource_id'),
    )
    
    # Action constants
    ACTION_CREATE = 'create'
    ACTION_UPDATE = 'update'
    ACTION_DELETE = 'delete'
    ACTION_LOGIN = 'login'
    ACTION_LOGOUT = 'logout'
    ACTION_PASSWORD_CHANGE = 'password_change'
    ACTION_PASSWORD_RESET = 'password_reset'
    ACTION_EXPORT = 'export'
    ACTION_IMPORT = 'import'
    ACTION_VIEW = 'view'
    
    @staticmethod
    def log_create(user_id, tenant_id, resource_type, resource_id, new_values=None):
        """Log record creation."""
        log = AuditLog(
            user_id=user_id,
            tenant_id=tenant_id,
            action=AuditLog.ACTION_CREATE,
            resource_type=resource_type,
            resource_id=resource_id,
            new_values=json.dumps(new_values) if new_values else None,
            status='success'
        )
        db.session.add(log)
        return log
    
    @staticmethod
    def log_update(user_id, tenant_id, resource_type, resource_id, old_values, new_values):
        """Log record update."""
        log = AuditLog(
            user_id=user_id,
            tenant_id=tenant_id,
            action=AuditLog.ACTION_UPDATE,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None,
            changes=json.dumps(AuditLog._compute_changes(old_values, new_values)),
            status='success'
        )
        db.session.add(log)
        return log
    
    @staticmethod
    def log_delete(user_id, tenant_id, resource_type, resource_id, old_values=None):
        """Log record deletion."""
        log = AuditLog(
            user_id=user_id,
            tenant_id=tenant_id,
            action=AuditLog.ACTION_DELETE,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=json.dumps(old_values) if old_values else None,
            status='success'
        )
        db.session.add(log)
        return log
    
    @staticmethod
    def log_login(user_id, tenant_id, success=True, error_message=None):
        """Log login attempt."""
        log = AuditLog(
            user_id=user_id,
            tenant_id=tenant_id,
            action=AuditLog.ACTION_LOGIN,
            resource_type='user',
            resource_id=user_id,
            status='success' if success else 'failure',
            error_message=error_message
        )
        db.session.add(log)
        return log
    
    @staticmethod
    def _compute_changes(old, new):
        """Compute differences between old and new values."""
        changes = {}
        old_dict = json.loads(old) if isinstance(old, str) else (old or {})
        new_dict = json.loads(new) if isinstance(new, str) else (new or {})
        
        for key in set(list(old_dict.keys()) + list(new_dict.keys())):
            old_val = old_dict.get(key)
            new_val = new_dict.get(key)
            if old_val != new_val:
                changes[key] = {'old': old_val, 'new': new_val}
        return changes
    
    def to_dict(self):
        """Serialize audit log."""
        data = super().to_dict()
        for field in ['old_values', 'new_values', 'changes']:
            if data.get(field):
                try:
                    data[field] = json.loads(data[field])
                except (json.JSONDecodeError, TypeError):
                    pass
        return data

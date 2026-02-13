"""
Webhook Models.

Stores webhook endpoints and delivery history.
"""
import hmac
import hashlib
import secrets
from datetime import datetime
from backend.extensions import db


class WebhookEndpoint(db.Model):
    """Webhook endpoint configuration."""
    __tablename__ = 'webhook_endpoints'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    secret = db.Column(db.String(64), nullable=False)
    events = db.Column(db.Text, nullable=False)  # JSON list of events to listen for
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    deliveries = db.relationship('WebhookDelivery', back_populates='endpoint', lazy='dynamic', cascade='all, delete-orphan')
    creator = db.relationship('User')
    
    def __repr__(self):
        return f'<WebhookEndpoint {self.name}: {self.url}>'
    
    def get_events(self):
        """Get list of events."""
        import json
        try:
            return json.loads(self.events)
        except:
            return []
    
    def set_events(self, events):
        """Set events from list."""
        import json
        self.events = json.dumps(events)
    
    def sign_payload(self, payload: str) -> str:
        """Generate HMAC signature for payload."""
        return hmac.new(
            self.secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
    
    @staticmethod
    def generate_secret():
        """Generate a new webhook secret."""
        return secrets.token_hex(32)


class WebhookDelivery(db.Model):
    """Webhook delivery attempt history."""
    __tablename__ = 'webhook_deliveries'
    
    id = db.Column(db.Integer, primary_key=True)
    endpoint_id = db.Column(db.Integer, db.ForeignKey('webhook_endpoints.id'), nullable=False)
    event = db.Column(db.String(100), nullable=False)
    payload = db.Column(db.Text)
    status_code = db.Column(db.Integer)
    response_body = db.Column(db.Text)
    error_message = db.Column(db.Text)
    attempts = db.Column(db.Integer, default=0)
    next_retry_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    endpoint = db.relationship('WebhookEndpoint', back_populates='deliveries')
    
    def __repr__(self):
        return f'<WebhookDelivery {self.event}: {self.status_code}>'
    
    @property
    def is_success(self):
        """Check if delivery was successful."""
        return 200 <= self.status_code < 300
    
    @property
    def is_pending(self):
        """Check if delivery is pending retry."""
        return self.next_retry_at is not None and self.next_retry_at > datetime.utcnow()


# Define available webhook events
class WebhookEvent:
    """Webhook event types."""
    
    # User events
    USER_CREATED = 'user.created'
    USER_UPDATED = 'user.updated'
    USER_DELETED = 'user.deleted'
    USER_LOGIN = 'user.login'
    
    # Project events
    PROJECT_CREATED = 'project.created'
    PROJECT_UPDATED = 'project.updated'
    PROJECT_DELETED = 'project.deleted'
    
    # Model events (No-Code Builder)
    MODEL_CREATED = 'model.created'
    MODEL_UPDATED = 'model.updated'
    MODEL_DELETED = 'model.deleted'
    
    # Data events (dynamic API)
    RECORD_CREATED = 'record.created'
    RECORD_UPDATED = 'record.updated'
    RECORD_DELETED = 'record.deleted'
    
    # Accounting events
    JOURNAL_ENTRY_CREATED = 'journal.created'
    JOURNAL_ENTRY_POSTED = 'journal.posted'
    INVOICE_CREATED = 'invoice.created'
    INVOICE_PAID = 'invoice.paid'
    
    # HR events
    EMPLOYEE_CREATED = 'employee.created'
    EMPLOYEE_UPDATED = 'employee.updated'
    LEAVE_REQUESTED = 'leave.requested'
    LEAVE_APPROVED = 'leave.approved'
    
    # All events
    ALL = '*'
    
    @classmethod
    def get_all_events(cls):
        """Get list of all available events."""
        return [
            cls.USER_CREATED, cls.USER_UPDATED, cls.USER_DELETED, cls.USER_LOGIN,
            cls.PROJECT_CREATED, cls.PROJECT_UPDATED, cls.PROJECT_DELETED,
            cls.MODEL_CREATED, cls.MODEL_UPDATED, cls.MODEL_DELETED,
            cls.RECORD_CREATED, cls.RECORD_UPDATED, cls.RECORD_DELETED,
            cls.JOURNAL_ENTRY_CREATED, cls.JOURNAL_ENTRY_POSTED,
            cls.INVOICE_CREATED, cls.INVOICE_PAID,
            cls.EMPLOYEE_CREATED, cls.EMPLOYEE_UPDATED,
            cls.LEAVE_REQUESTED, cls.LEAVE_APPROVED,
        ]
    
    @classmethod
    def get_categories(cls):
        """Get events grouped by category."""
        return {
            'user': [cls.USER_CREATED, cls.USER_UPDATED, cls.USER_DELETED, cls.USER_LOGIN],
            'project': [cls.PROJECT_CREATED, cls.PROJECT_UPDATED, cls.PROJECT_DELETED],
            'model': [cls.MODEL_CREATED, cls.MODEL_UPDATED, cls.MODEL_DELETED],
            'data': [cls.RECORD_CREATED, cls.RECORD_UPDATED, cls.RECORD_DELETED],
            'accounting': [cls.JOURNAL_ENTRY_CREATED, cls.JOURNAL_ENTRY_POSTED, cls.INVOICE_CREATED, cls.INVOICE_PAID],
            'hr': [cls.EMPLOYEE_CREATED, cls.EMPLOYEE_UPDATED, cls.LEAVE_REQUESTED, cls.LEAVE_APPROVED],
        }

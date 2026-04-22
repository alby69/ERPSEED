"""
Base models with multi-tenant support.
All models inherit from BaseModel which includes basic fields and utility methods.
"""
from datetime import datetime
from backend.extensions import db


class BaseModel(db.Model):
    """
    Base class for all database models.
    Includes:
    - id: Primary key
    - created_at: Creation timestamp
    - updated_at: Last update timestamp
    - deleted_at: Soft delete timestamp
    """
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def soft_delete(self):
        """Mark record as deleted without removing."""
        self.deleted_at = datetime.utcnow()
        db.session.add(self)

    def restore(self):
        """Restore soft-deleted record."""
        self.deleted_at = None
        db.session.add(self)

    @classmethod
    def active(cls):
        """Return only records that are not soft-deleted."""
        return cls.query.filter_by(deleted_at=None)

    def to_dict(self, exclude=None):
        """Convert model to dictionary."""
        exclude = exclude or []
        result = {}
        for col in self.__table__.columns:
            if col.name in exclude:
                continue
            value = getattr(self, col.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            elif hasattr(value, 'isoformat'):
                value = value.isoformat()
            result[col.name] = value
        return result


class TimestampMixin:
    """Mixin for tracking who created/updated records."""

    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Note: Use lazy imports or string references to avoid circular dependency with User model
    created_by = db.relationship('User', foreign_keys=[created_by_id], lazy='joined')
    updated_by = db.relationship('User', foreign_keys=[updated_by_id], lazy='joined')

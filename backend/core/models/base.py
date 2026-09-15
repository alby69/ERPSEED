"""
Base models with multi-tenant support.
All models inherit from BaseModel which includes basic fields and utility methods.
"""
from datetime import datetime, timezone
from backend.extensions import db
from backend.core.models.mixins import TenantMixin, TimestampMixin, SoftDeleteMixin


class BaseModel(db.Model, SoftDeleteMixin):
    """
    Base class for all database models.
    Includes:
    - id: Primary key
    - created_at: Creation timestamp
    - updated_at: Last update timestamp
    - deleted_at: Soft delete timestamp (for soft deletion support)
    """
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

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


class CoreEntityMixin(TenantMixin, TimestampMixin, SoftDeleteMixin):
    """
    Unified mixin combining multi-tenancy, creation/update timestamps/user-tracking, and soft deletion.
    """
    pass


# Re-export mixins for backward compatibility
__all__ = ["BaseModel", "TenantMixin", "TimestampMixin", "SoftDeleteMixin", "CoreEntityMixin"]

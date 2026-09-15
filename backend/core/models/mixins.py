"""
Core Model Mixins for ERPSEED.
Provides reusable model mixins for multi-tenancy, timestamps, audit user tracking, and soft deletion.
"""
from datetime import datetime, timezone
from sqlalchemy.orm import declared_attr
from backend.extensions import db


class TenantMixin:
    """
    Mixin for row-level multi-tenancy isolation.
    Adds tenant_id column with foreign key to tenants table.
    """
    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )


class TimestampMixin:
    """
    Mixin for creation, update, and user tracking timestamps.
    """
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    @declared_attr
    def created_by(cls):
        return db.relationship('User', foreign_keys=[cls.created_by_id], lazy='joined')

    @declared_attr
    def updated_by(cls):
        return db.relationship('User', foreign_keys=[cls.updated_by_id], lazy='joined')


class SoftDeleteMixin:
    """
    Mixin for soft delete functionality.
    """
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def soft_delete(self):
        """Mark record as soft-deleted."""
        self.deleted_at = datetime.now(timezone.utc)
        db.session.add(self)

    def restore(self):
        """Restore soft-deleted record."""
        self.deleted_at = None
        db.session.add(self)

    @classmethod
    def active(cls):
        """Return query filter for non-deleted records."""
        return cls.query.filter_by(deleted_at=None)


class CoreEntityMixin(TenantMixin, TimestampMixin, SoftDeleteMixin):
    """
    Unified mixin combining multi-tenancy, creation/update timestamps/user-tracking, and soft deletion.
    """
    pass


__all__ = ["TenantMixin", "TimestampMixin", "SoftDeleteMixin", "CoreEntityMixin"]

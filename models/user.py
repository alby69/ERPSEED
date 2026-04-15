from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from extensions import db
from .base import BaseModel
from .project import project_members


class User(BaseModel):
    """User model for system users."""

    __tablename__ = "users"

    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id"), nullable=True, index=True
    )

    email = db.Column(db.String(120), nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    role = db.Column(
        db.String(80),
        default="user",
        nullable=False,
        comment="User role (e.g., admin, user)",
    )
    is_active = db.Column(db.Boolean, default=True)
    force_password_change = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.String(255), nullable=True)

    is_primary = db.Column(db.Boolean, default=False, comment="Primary admin of tenant")
    last_login_at = db.Column(db.DateTime)
    login_count = db.Column(db.Integer, default=0)
    password_reset_token = db.Column(db.String(255))
    password_reset_expires = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)

    tenant = db.relationship(
        "Tenant", backref=db.backref("tenant_users", lazy="dynamic")
    )
    projects = db.relationship(
        "Project", secondary=project_members, back_populates="members", lazy="dynamic"
    )
    tenant_members = db.relationship(
        "TenantMember",
        back_populates="user",
        foreign_keys="TenantMember.userId",
        lazy="dynamic",
    )
    project_memberships = db.relationship(
        "TenantMember",
        secondary=project_members,
        primaryjoin="User.id == project_members.c.userId",
        secondaryjoin="TenantMember.userId == project_members.c.userId",
        viewonly=True,
    )

    __table_args__ = (
        db.UniqueConstraint("tenant_id", "email", name="uix_tenant_email"),
    )

    def __repr__(self):
        return f"<User {self.email}>"

    @property
    def full_name(self):
        full = f"{self.first_name or ''} {self.last_name or ''}".strip()
        return full or self.email

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        self.force_password_change = False
        self.password_reset_token = None
        self.password_reset_expires = None

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def record_login(self):
        """Record user login."""
        self.last_login_at = datetime.datetime.utcnow()
        self.login_count += 1

    def to_dict(self, include_email=True):
        """Serialize user."""
        def format_datetime(value):
            if value is None:
                return None
            if isinstance(value, str):
                return value
            return value.isoformat()

        result = {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "role": self.role,
            "is_active": self.is_active,
            "is_primary": self.is_primary,
            "tenant_id": self.tenant_id,
            "created_at": format_datetime(self.created_at),
            "updated_at": format_datetime(self.updated_at),
        }
        if not include_email:
            result.pop("email", None)
        return result

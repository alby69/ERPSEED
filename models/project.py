from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from extensions import db
from .base import BaseModel


project_members = db.Table(
    "project_members",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("project_id", db.Integer, db.ForeignKey("projects.id"), primary_key=True),
)


class Project(BaseModel):
    """
    Represents a Project or application instance created with the Builder.
    Each project is a container for a set of models (SysModel).
    """

    __tablename__ = "projects"
    name = db.Column(
        db.String(80),
        unique=True,
        nullable=False,
        comment="Internal project name (e.g., 'fleet_management')",
    )
    title = db.Column(
        db.String(120), nullable=False, comment="Display title for the project"
    )
    description = db.Column(db.Text)
    version = db.Column(db.String(20), default="1.0.0", comment="Project version")
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    primary_color = db.Column(db.String(20), default="#1677ff")
    border_radius = db.Column(db.Integer, default=6)
    theme_mode = db.Column(db.String(20), default="light")

    models = db.relationship(
        "SysModel",
        back_populates="project",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    owner = db.relationship("User")
    members = db.relationship(
        "User", secondary=project_members, back_populates="projects", lazy="dynamic"
    )
    user_memberships = db.relationship(
        "TenantMember",
        secondary=project_members,
        primaryjoin="Project.id == project_members.c.project_id",
        secondaryjoin="TenantMember.user_id == project_members.c.user_id",
        viewonly=True,
    )

    def __repr__(self):
        return f"<Project {self.name}>"

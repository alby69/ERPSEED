"""
Module - Sistema di modularizzazione per ERPSeed.

Un Module è un'unità logica che raggruppa:
- SysModel (tabelle dati)
- Block/Component (interfacce UI)
- API endpoints

Workflow: Draft → Testing → Published → (opzionalmente) Deprecated

Tipi:
- system: Moduli core del sistema (non eliminabili)
- custom: Moduli creati dagli utenti
- package: Pacchetto contenente più moduli
"""

from backend.core.models.base import BaseModel
from backend.extensions import db
from backend.infrastructure.builder.models import Block  # noqa: F401 - needed for SQLAlchemy relationship

module_models = db.Table(
    "module_models",
    db.Column("module_id", db.Integer, db.ForeignKey("modules.id"), primary_key=True),
    db.Column(
        "sysmodel_id", db.Integer, db.ForeignKey("sys_models.id"), primary_key=True
    ),
    info={"bind_key": None},
)

module_blocks = db.Table(
    "module_blocks",
    db.Column("module_id", db.Integer, db.ForeignKey("modules.id"), primary_key=True),
    db.Column("block_id", db.Integer, db.ForeignKey("blocks.id"), primary_key=True),
    info={"bind_key": None},
)

# Package: moduli contenuti in un pacchetto
module_packages = db.Table(
    "module_packages",
    db.Column("package_id", db.Integer, db.ForeignKey("modules.id"), primary_key=True),
    db.Column(
        "contained_module_id", db.Integer, db.ForeignKey("modules.id"), primary_key=True
    ),
    info={"bind_key": None},
)

# Module ↔ Project: quali moduli sono assegnati a quali progetti
module_projects = db.Table(
    "module_projects",
    db.Column("module_id", db.Integer, db.ForeignKey("modules.id"), primary_key=True),
    db.Column("project_id", db.Integer, db.ForeignKey("projects.id"), primary_key=True),
    db.Column("is_enabled", db.Boolean, default=True),
    db.Column("assigned_at", db.DateTime, default=db.func.now()),
    info={"bind_key": None},
)


class Module(BaseModel):
    """
    Rappresenta un modulo applicativo completo.
    """

    __tablename__ = "modules"

    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)

    # Tipo: system, custom, package
    type = db.Column(db.String(20), default="custom", nullable=False, index=True)

    # Se true, è un modulo core (non eliminabile)
    is_core = db.Column(db.Boolean, default=False, nullable=False)

    # Workflow: draft, testing, published, deprecated
    status = db.Column(db.String(20), default="draft", nullable=False, index=True)

    # Category: core, builtin, premium, third_party
    category = db.Column(db.String(20), default="builtin", nullable=False)

    # Licensing
    is_free = db.Column(db.Boolean, default=True)
    price = db.Column(db.Numeric(10, 2))
    plan_required = db.Column(db.String(50), default="starter")

    # Version
    version = db.Column(db.String(20), default="1.0.0")
    core_version_min = db.Column(db.String(20), default="1.0.0")

    # Dependencies
    dependencies = db.Column(db.JSON, default=list)

    # Test
    test_suite_id = db.Column(db.Integer, db.ForeignKey("test_suites.id"))
    test_results = db.Column(db.JSON, default=dict)
    quality_score = db.Column(db.Float, default=0.0)

    # UI Configuration
    icon = db.Column(db.String(50), default="box")
    menu_position = db.Column(db.Integer, default=100)

    # API Definition
    api_definition = db.Column(db.JSON, default=dict)

    # Relazioni
    models = db.relationship(
        "SysModel",
        secondary=module_models,
        backref=db.backref("modules", lazy="dynamic"),
        lazy="select",
    )
    blocks = db.relationship(
        "Block",
        secondary=module_blocks,
        backref=db.backref("modules", lazy="dynamic"),
        lazy="select",
    )

    # Progetti a cui è assegnato il modulo
    projects = db.relationship(
        "Project",
        secondary=module_projects,
        backref=db.backref("assigned_modules", lazy="dynamic"),
        lazy="select",
    )

    # Se package, contiene altri moduli (self-referential many-to-many)
    contained_modules = db.relationship(
        "Module",
        secondary=module_packages,
        primaryjoin="Module.id==module_packages.c.package_id",
        secondaryjoin="Module.id==module_packages.c.contained_module_id",
        backref=db.backref("packages", lazy="dynamic"),
        lazy="select",
    )

    __table_args__ = (db.Index("ix_modules_type_status", "type", "status"),)

    def __repr__(self):
        return f"<Module {self.name}>"

    def to_dict(self, include_relations=False):
        """Serialize module."""
        result = {
            "id": self.id,
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "type": self.type,
            "is_core": self.is_core,
            "status": self.status,
            "category": self.category,
            "is_free": self.is_free,
            "price": float(self.price) if self.price else None,
            "plan_required": self.plan_required,
            "version": self.version,
            "core_version_min": self.core_version_min,
            "dependencies": self.dependencies or [],
            "test_suite_id": self.test_suite_id,
            "test_results": self.test_results or {},
            "quality_score": self.quality_score,
            "icon": self.icon,
            "menu_position": self.menu_position,
            "api_definition": self.api_definition or {},
            "project_ids": [p.id for p in self.projects],
            "contained_module_ids": [m.id for m in self.contained_modules],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_relations:
            result["models"] = [m.to_dict() for m in self.models]
            result["blocks"] = [b.to_dict() for b in self.blocks]
            result["projects"] = [{"id": p.id, "name": p.name} for p in self.projects]
            result["contained_modules"] = [
                {"id": m.id, "name": m.name, "title": m.title}
                for m in self.contained_modules
            ]

        return result

    @property
    def is_published(self):
        return self.status == "published"

    @property
    def is_package(self):
        return self.type == "package"

    @property
    def can_delete(self):
        """Check if module can be deleted."""
        if self.is_core:
            return False, "Non è possibile eliminare un modulo core"
        if self.status == "published":
            return (
                False,
                "Non è possibile eliminare un modulo pubblicato. Revoca prima la pubblicazione.",
            )
        return True, "OK"

    @property
    def can_modify(self):
        """Check if module can be modified."""
        if self.is_core:
            return False, "Non è possibile modificare un modulo core"
        if self.status == "published":
            return (
                False,
                "Non è possibile modificare un modulo pubblicato. Revoca prima la pubblicazione.",
            )
        return True, "OK"

    @property
    def can_publish(self):
        """Check if module can be published."""
        if self.status != "testing":
            return False, "Il modulo deve essere in stato 'testing'"

        if self.quality_score < 80:
            return False, f"Quality score insufficiente ({self.quality_score} < 80%)"

        if not self.models or not any(b for b in self.blocks if b.view_type):
            return False, "Il modulo deve avere almeno un modello e una vista"

        return True, "OK"

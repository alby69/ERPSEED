"""
CQRS Commands for Schema-as-Code Scaffold Engine.
Defines domain commands dispatched during declarative template materialization.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from backend.shared.commands import Command


@dataclass
class RegisterEntityCommand(Command):
    """
    Command to register or update an entity definition in the dynamic ER engine (SysModel/SysField).
    """
    module: str = ""
    entity: str = ""
    extends: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    fields: List[Dict[str, Any]] = field(default_factory=list)
    relations: List[Dict[str, Any]] = field(default_factory=list)
    permissions: Dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> Dict[str, Any]:
        """Returns payload representation for event bus broadcasting."""
        return {
            "module": self.module,
            "entity": self.entity,
            "extends": self.extends,
            "metadata": self.metadata,
            "fields": self.fields,
            "relations": self.relations,
            "permissions": self.permissions,
        }

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update(self.to_payload())
        return d


@dataclass
class DefineRelationCommand(Command):
    """
    Command to define an entity relationship in the system.
    """
    module: str = ""
    entity: str = ""
    relation_name: str = ""
    target: str = ""
    relation_type: str = ""
    cascade: Optional[str] = None
    ui_config: Dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> Dict[str, Any]:
        return {
            "module": self.module,
            "entity": self.entity,
            "relation_name": self.relation_name,
            "target": self.target,
            "relation_type": self.relation_type,
            "cascade": self.cascade,
            "ui_config": self.ui_config,
        }

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update(self.to_payload())
        return d


@dataclass
class ScaffoldBackendCommand(Command):
    """
    Command to trigger backend code scaffolding (SQLAlchemy models, Marshmallow schemas, CQRS handlers).
    """
    module: str = ""
    entity: str = ""
    fields: List[Dict[str, Any]] = field(default_factory=list)
    relations: List[Dict[str, Any]] = field(default_factory=list)

    def to_payload(self) -> Dict[str, Any]:
        return {
            "module": self.module,
            "entity": self.entity,
            "fields": self.fields,
            "relations": self.relations,
        }

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update(self.to_payload())
        return d


@dataclass
class ScaffoldFrontendCommand(Command):
    """
    Command to trigger frontend code scaffolding (Ant Design pages, form validation, API clients).
    """
    module: str = ""
    entity: str = ""
    fields: List[Dict[str, Any]] = field(default_factory=list)
    relations: List[Dict[str, Any]] = field(default_factory=list)

    def to_payload(self) -> Dict[str, Any]:
        return {
            "module": self.module,
            "entity": self.entity,
            "fields": self.fields,
            "relations": self.relations,
        }

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update(self.to_payload())
        return d


@dataclass
class GenerateMigrationCommand(Command):
    """
    Command to prepare database migrations (Alembic) for new or modified entity schemas.
    """
    module: str = ""
    entity: str = ""

    def to_payload(self) -> Dict[str, Any]:
        return {
            "module": self.module,
            "entity": self.entity,
        }

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update(self.to_payload())
        return d

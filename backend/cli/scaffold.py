"""
CLI Module Scaffolder for ERPSEED.
Supports generating simple (BaseService + CRUD) and complex (CQRS) module structures.

Usage:
    python -m backend.cli scaffold_module --name Vehicle --type simple|cqrs
"""

import argparse
import os
from pathlib import Path


SIMPLE_MODELS_TEMPLATE = '''"""
{name} SQLAlchemy Models.
"""
from backend.core.models.base import BaseModel
from backend.core.models.mixins import CoreEntityMixin
from backend.extensions import db


class {name}(BaseModel, CoreEntityMixin):
    __tablename__ = "{snake_name}s"

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<{name} {{self.name}} (ID: {{self.id}})>"
'''

SIMPLE_SCHEMAS_TEMPLATE = '''"""
{name} Marshmallow Schemas.
"""
from marshmallow import fields, Schema


class {name}Schema(Schema):
    id = fields.Int(dump_only=True)
    tenant_id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    is_active = fields.Bool(dump_default=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class {name}CreateSchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    is_active = fields.Bool(dump_default=True)
'''

SIMPLE_SERVICES_TEMPLATE = '''"""
{name} Service layer using BaseService.
"""
from backend.core.services.base import BaseService
from backend.modules.{module_dir}.models import {name}


class {name}Service(BaseService[{name}]):
    def __init__(self):
        super().__init__({name})


{snake_name}_service = {name}Service()
'''

SIMPLE_API_TEMPLATE = '''"""
{name} REST API Endpoints.
"""
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.modules.{module_dir}.models import {name}
from backend.modules.{module_dir}.schemas import {name}Schema, {name}CreateSchema
from backend.modules.{module_dir}.services import {snake_name}_service

blp = Blueprint(
    "{snake_name}s",
    __name__,
    url_prefix="/api/v1/{snake_name}s",
    description="{name} management operations"
)


@{snake_name}_bp_route = blp


@blp.route("", methods=["GET"])
@jwt_required()
@blp.response(200, {name}Schema(many=True))
def list_{snake_name}s():
    user = get_jwt_identity()
    tenant_id = user.get("tenant_id")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    return {snake_name}_service.get_multi(tenant_id=tenant_id, page=page, per_page=per_page)


@blp.route("", methods=["POST"])
@jwt_required()
@blp.arguments({name}CreateSchema)
@blp.response(201, {name}Schema)
def create_{snake_name}(data):
    user = get_jwt_identity()
    tenant_id = user.get("tenant_id")
    return {snake_name}_service.create(data, tenant_id=tenant_id)


@blp.route("/<int:entity_id>", methods=["GET"])
@jwt_required()
@blp.response(200, {name}Schema)
def get_{snake_name}(entity_id):
    user = get_jwt_identity()
    tenant_id = user.get("tenant_id")
    entity = {snake_name}_service.get_by_id(entity_id, tenant_id=tenant_id)
    if not entity:
        abort(404, message="{name} not found")
    return entity


@blp.route("/<int:entity_id>", methods=["PUT"])
@jwt_required()
@blp.arguments({name}CreateSchema)
@blp.response(200, {name}Schema)
def update_{snake_name}(data, entity_id):
    user = get_jwt_identity()
    tenant_id = user.get("tenant_id")
    entity = {snake_name}_service.update(entity_id, data, tenant_id=tenant_id)
    if not entity:
        abort(404, message="{name} not found")
    return entity


@blp.route("/<int:entity_id>", methods=["DELETE"])
@jwt_required()
def delete_{snake_name}(entity_id):
    user = get_jwt_identity()
    tenant_id = user.get("tenant_id")
    success = {snake_name}_service.delete(entity_id, tenant_id=tenant_id)
    if not success:
        abort(404, message="{name} not found")
    return {{"message": "{name} deleted successfully"}}, 200
'''

CQRS_DOMAIN_MODELS_TEMPLATE = '''"""
{name} Domain Models.
"""
from backend.core.models.base import BaseModel
from backend.core.models.mixins import CoreEntityMixin
from backend.extensions import db


class {name}(BaseModel, CoreEntityMixin):
    __tablename__ = "{snake_name}s"

    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(30), default="draft", nullable=False)
'''

CQRS_DOMAIN_EVENTS_TEMPLATE = '''"""
{name} Domain Events.
"""
from backend.shared.events import DomainEvent


class {name}CreatedEvent(DomainEvent):
    def __init__(self, {snake_name}_id: int, payload: dict, tenant_id: int):
        super().__init__(
            event_type="{snake_name}.created",
            payload={{"{snake_name}_id": {snake_name}_id, **payload}},
            tenant_id=tenant_id
        )


class {name}UpdatedEvent(DomainEvent):
    def __init__(self, {snake_name}_id: int, payload: dict, tenant_id: int):
        super().__init__(
            event_type="{snake_name}.updated",
            payload={{"{snake_name}_id": {snake_name}_id, **payload}},
            tenant_id=tenant_id
        )
'''

CQRS_COMMANDS_TEMPLATE = '''"""
{name} Commands.
"""
from backend.shared.commands import Command


class Create{name}Command(Command):
    def __init__(self, name: str, code: str, tenant_id: int):
        super().__init__(tenant_id=tenant_id)
        self.name = name
        self.code = code

    def to_payload(self) -> dict:
        return {{"name": self.name, "code": self.code}}
'''

CQRS_QUERIES_TEMPLATE = '''"""
{name} Queries.
"""
from backend.shared.commands import Command


class Get{name}Query(Command):
    def __init__(self, entity_id: int, tenant_id: int):
        super().__init__(tenant_id=tenant_id)
        self.entity_id = entity_id
'''

CQRS_HANDLERS_TEMPLATE = '''"""
{name} Command & Query Handlers.
"""
from backend.shared.handlers import CreateHandler, QueryHandler, CommandResult
from backend.shared.commands import Command
from backend.modules.{module_dir}.application.commands import Create{name}Command
from backend.modules.{module_dir}.application.queries import Get{name}Query
from backend.modules.{module_dir}.domain.events import {name}CreatedEvent


class Create{name}Handler(CreateHandler):
    def __init__(self, repository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus

    @property
    def command_type(self) -> str:
        return "Create{name}"

    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, Create{name}Command):
            return CommandResult.error("Invalid command type")

        result = self.repository.create({**command.to_payload(), "tenant_id": command.tenant_id})
        if self.event_bus:
            self.event_bus.publish({name}CreatedEvent(result["id"], result, command.tenant_id))
        return CommandResult.ok(result)


class Get{name}Handler(QueryHandler):
    def __init__(self, repository, event_bus=None):
        self.repository = repository

    @property
    def command_type(self) -> str:
        return "Get{name}"

    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, Get{name}Query):
            return CommandResult.error("Invalid query type")

        entity = self.repository.find_by_id(command.entity_id, command.tenant_id)
        if not entity:
            return CommandResult.error("{name} not found")
        return CommandResult.ok(entity)
'''

CQRS_REPOSITORY_TEMPLATE = '''"""
{name} Infrastructure Repository.
"""
from backend.extensions import db
from backend.modules.{module_dir}.domain.models import {name}


class {name}Repository:
    def create(self, data: dict) -> dict:
        entity = {name}(**data)
        db.session.add(entity)
        db.session.commit()
        return entity.to_dict()

    def find_by_id(self, entity_id: int, tenant_id: int) -> dict:
        entity = {name}.query.filter_by(id=entity_id, tenant_id=tenant_id).first()
        return entity.to_dict() if entity else None
'''

CQRS_ROUTES_TEMPLATE = '''"""
{name} CQRS API Routes.
"""
from flask import request, jsonify
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.modules.{module_dir}.application.commands import Create{name}Command
from backend.modules.{module_dir}.application.queries import Get{name}Query
from backend.modules.{module_dir}.container import {snake_name}_container

blp = Blueprint(
    "{snake_name}s_cqrs",
    __name__,
    url_prefix="/api/v1/{snake_name}s",
    description="{name} CQRS management"
)


@blp.route("", methods=["POST"])
@jwt_required()
def create_{snake_name}():
    user = get_jwt_identity()
    data = request.get_json() or {{}}
    cmd = Create{name}Command(
        name=data.get("name"),
        code=data.get("code"),
        tenant_id=user.get("tenant_id")
    )
    handler = {snake_name}_container.get_handler("Create{name}")
    res = handler.handle(cmd)
    if not res.success:
        return jsonify({{"error": res.error}}), 400
    return jsonify(res.data), 201


@blp.route("/<int:entity_id>", methods=["GET"])
@jwt_required()
def get_{snake_name}(entity_id):
    user = get_jwt_identity()
    query = Get{name}Query(entity_id=entity_id, tenant_id=user.get("tenant_id"))
    handler = {snake_name}_container.get_handler("Get{name}")
    res = handler.handle(query)
    if not res.success:
        return jsonify({{"error": res.error}}), 404
    return jsonify(res.data), 200
'''

CQRS_CONTAINER_TEMPLATE = '''"""
{name} CQRS Dependency Injection Container.
"""
from backend.modules.{module_dir}.infrastructure.repository import {name}Repository
from backend.modules.{module_dir}.application.handlers import Create{name}Handler, Get{name}Handler
from backend.shared.events import get_event_bus


class {name}Container:
    def __init__(self):
        self.repository = {name}Repository()
        self.event_bus = get_event_bus()
        self.handlers = {{
            "Create{name}": Create{name}Handler(self.repository, self.event_bus),
            "Get{name}": Get{name}Handler(self.repository, self.event_bus),
        }}

    def get_handler(self, command_name: str):
        return self.handlers.get(command_name)


{snake_name}_container = {name}Container()
'''


def to_snake_case(name: str) -> str:
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def scaffold_module(name: str, module_type: str = "simple", target_dir: str = None) -> str:
    """
    Generates module scaffolding.
    """
    snake_name = to_snake_case(name)
    module_dir_name = snake_name

    root = Path(__file__).resolve().parent.parent.parent
    base_path = Path(target_dir) if target_dir else root / "backend" / "modules" / module_dir_name

    if base_path.exists():
        raise ValueError(f"Module directory already exists: {base_path}")

    base_path.mkdir(parents=True, exist_ok=True)

    context = {
        "name": name,
        "snake_name": snake_name,
        "module_dir": module_dir_name
    }

    if module_type == "simple":
        (base_path / "__init__.py").write_text(f'"""{name} Simple Module."""\n')
        (base_path / "models.py").write_text(SIMPLE_MODELS_TEMPLATE.format(**context))
        (base_path / "schemas.py").write_text(SIMPLE_SCHEMAS_TEMPLATE.format(**context))
        (base_path / "services.py").write_text(SIMPLE_SERVICES_TEMPLATE.format(**context))
        (base_path / "api.py").write_text(SIMPLE_API_TEMPLATE.format(**context))
    elif module_type == "cqrs":
        (base_path / "__init__.py").write_text(f'"""{name} CQRS Module."""\n')

        # Domain
        domain_path = base_path / "domain"
        domain_path.mkdir(parents=True, exist_ok=True)
        (domain_path / "__init__.py").write_text('from .models import *\nfrom .events import *\n')
        (domain_path / "models.py").write_text(CQRS_DOMAIN_MODELS_TEMPLATE.format(**context))
        (domain_path / "events.py").write_text(CQRS_DOMAIN_EVENTS_TEMPLATE.format(**context))

        # Application
        app_path = base_path / "application"
        app_path.mkdir(parents=True, exist_ok=True)
        (app_path / "__init__.py").write_text('from .commands import *\nfrom .queries import *\nfrom .handlers import *\n')
        (app_path / "commands.py").write_text(CQRS_COMMANDS_TEMPLATE.format(**context))
        (app_path / "queries.py").write_text(CQRS_QUERIES_TEMPLATE.format(**context))
        (app_path / "handlers.py").write_text(CQRS_HANDLERS_TEMPLATE.format(**context))

        # Infrastructure
        infra_path = base_path / "infrastructure"
        infra_path.mkdir(parents=True, exist_ok=True)
        (infra_path / "__init__.py").write_text('from .repository import *\n')
        (infra_path / "repository.py").write_text(CQRS_REPOSITORY_TEMPLATE.format(**context))

        # API & Container
        api_path = base_path / "api"
        api_path.mkdir(parents=True, exist_ok=True)
        (api_path / "__init__.py").write_text('from .routes import blp\n')
        (api_path / "routes.py").write_text(CQRS_ROUTES_TEMPLATE.format(**context))

        (base_path / "container.py").write_text(CQRS_CONTAINER_TEMPLATE.format(**context))
    else:
        raise ValueError(f"Invalid module type: {module_type}. Must be 'simple' or 'cqrs'.")

    return str(base_path)


def main():
    parser = argparse.ArgumentParser(description="Scaffold a new module for ERPSEED.")
    parser.add_argument("command", nargs="?", default="scaffold_module", help="Command to run (e.g. scaffold_module)")
    parser.add_argument("--name", required=True, help="Name of the module entity (e.g. Vehicle)")
    parser.add_argument("--type", choices=["simple", "cqrs"], default="simple", help="Type of module architecture")

    args = parser.parse_args()
    path = scaffold_module(args.name, args.type)
    print(f"Successfully scaffolded {args.type} module '{args.name}' at: {path}")


if __name__ == "__main__":
    main()

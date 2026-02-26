"""
Builder API - Archetype, Component, Block
REST API for managing components and blocks
"""

from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import select
from marshmallow import Schema, fields

from backend.extensions import db
from backend.builder.models import (
    Archetype,
    Component,
    Block,
    BlockRelationship,
    create_system_archetypes,
)

blp = Blueprint(
    "component_builder",
    __name__,
    url_prefix="/api",
    description="Component Builder API",
)


# === SCHEMAS ===


class ArchetypeCreateSchema(Schema):
    name = fields.String(required=True)
    component_type = fields.String(required=True)
    description = fields.String()
    icon = fields.String()
    default_config = fields.Dict()
    api_schema = fields.Dict()


class ComponentCreateSchema(Schema):
    archetype_id = fields.Integer(required=True)
    name = fields.String(required=True)
    description = fields.String()
    config = fields.Dict()
    position_x = fields.Integer()
    position_y = fields.Integer()
    width = fields.Integer()
    height = fields.Integer()
    order_index = fields.Integer()
    block_id = fields.Integer()


class BlockCreateSchema(Schema):
    name = fields.String(required=True)
    description = fields.String()
    config = fields.Dict()


class BlockRelationshipSchema(Schema):
    source_component_id = fields.Integer(required=True)
    target_component_id = fields.Integer(required=True)
    relationship_type = fields.String(required=True)
    config = fields.Dict()


# === ARCHETYPES ===


@blp.route("/archetypes")
class ArchetypeList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def get(self):
        """List all system archetypes"""
        archetypes = Archetype.query.all()
        return [
            {
                "id": a.id,
                "name": a.name,
                "component_type": a.component_type,
                "description": a.description,
                "icon": a.icon,
                "is_system": a.is_system,
                "default_config": a.default_config,
                "api_schema": a.api_schema,
            }
            for a in archetypes
        ]


@blp.route("/archetypes/<int:archetype_id>")
class ArchetypeDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def get(self, archetype_id):
        """Get archetype details"""
        archetype = Archetype.query.get_or_404(archetype_id)
        return {
            "id": archetype.id,
            "name": archetype.name,
            "component_type": archetype.component_type,
            "description": archetype.description,
            "icon": archetype.icon,
            "is_system": archetype.is_system,
            "default_config": archetype.default_config,
            "api_schema": archetype.api_schema,
        }


# === COMPONENTS ===


@blp.route("/projects/<int:project_id>/components")
class ComponentList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def get(self, project_id):
        """List all components in a project"""
        components = Component.query.filter_by(project_id=project_id).all()
        return [
            {
                "id": c.id,
                "name": c.name,
                "description": c.description,
                "archetype_id": c.archetype_id,
                "archetype_name": c.archetype.name if c.archetype else None,
                "component_type": c.archetype.component_type if c.archetype else None,
                "config": c.config,
                "position_x": c.position_x,
                "position_y": c.position_y,
                "width": c.width,
                "height": c.height,
                "order_index": c.order_index,
                "block_id": c.block_id,
            }
            for c in components
        ]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(ComponentCreateSchema)
    @blp.response(201)
    def post(self, project_id, component_data):
        """Create a new component"""
        component = Component(
            project_id=project_id,
            archetype_id=component_data.get("archetype_id"),
            name=component_data.get("name"),
            description=component_data.get("description"),
            config=component_data.get("config", {}),
            position_x=component_data.get("position_x", 0),
            position_y=component_data.get("position_y", 0),
            width=component_data.get("width", 6),
            height=component_data.get("height", 4),
            order_index=component_data.get("order_index", 0),
        )
        db.session.add(component)
        db.session.commit()
        return {"id": component.id, "message": "Component created"}


@blp.route("/components/<int:component_id>")
class ComponentDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def get(self, component_id):
        """Get component details"""
        component = Component.query.get_or_404(component_id)
        return {
            "id": component.id,
            "project_id": component.project_id,
            "archetype_id": component.archetype_id,
            "name": component.name,
            "description": component.description,
            "config": component.config,
            "position_x": component.position_x,
            "position_y": component.position_y,
            "width": component.width,
            "height": component.height,
            "order_index": component.order_index,
            "block_id": component.block_id,
        }

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(ComponentCreateSchema)
    @blp.response(200)
    def put(self, component_id, component_data):
        """Update component"""
        component = Component.query.get_or_404(component_id)

        for key in [
            "name",
            "description",
            "config",
            "position_x",
            "position_y",
            "width",
            "height",
            "order_index",
        ]:
            if key in component_data:
                setattr(component, key, component_data[key])

        db.session.commit()
        return {"id": component.id, "message": "Component updated"}

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, component_id):
        """Delete component"""
        component = Component.query.get_or_404(component_id)
        db.session.delete(component)
        db.session.commit()
        return ""


@blp.route("/components/<int:component_id>/position")
class ComponentPosition(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(ComponentCreateSchema)
    @blp.response(200)
    def put(self, component_id, component_data):
        """Update component position"""
        component = Component.query.get_or_404(component_id)

        component.position_x = component_data.get("position_x", component.position_x)
        component.position_y = component_data.get("position_y", component.position_y)
        component.width = component_data.get("width", component.width)
        component.height = component_data.get("height", component.height)

        db.session.commit()
        return {"id": component.id, "message": "Position updated"}


# === BLOCKS ===


@blp.route("/projects/<int:project_id>/blocks")
class BlockList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def get(self, project_id):
        """List all blocks in a project"""
        blocks = Block.query.filter_by(project_id=project_id).all()
        return [
            {
                "id": b.id,
                "name": b.name,
                "description": b.description,
                "version": b.version,
                "status": b.status,
                "quality_score": b.quality_score,
                "is_certified": b.is_certified,
                "component_count": len(b.component_ids) if b.component_ids else 0,
                "created_at": b.created_at.isoformat() if b.created_at else None,
            }
            for b in blocks
        ]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(BlockCreateSchema)
    @blp.response(201)
    def post(self, project_id, block_data):
        """Create a new block"""
        user_id = get_jwt_identity()

        block = Block(
            project_id=project_id,
            created_by=user_id,
            name=block_data.get("name"),
            description=block_data.get("description"),
            component_ids=block_data.get("component_ids", []),
            relationships=block_data.get("relationships", {}),
            api_endpoints=block_data.get("api_endpoints", []),
            version=block_data.get("version", "1.0.0"),
            status="draft",
        )
        db.session.add(block)
        db.session.commit()
        return {"id": block.id, "message": "Block created"}


@blp.route("/blocks/<int:block_id>")
class BlockDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def get(self, block_id):
        """Get block details with components"""
        block = Block.query.get_or_404(block_id)

        # Get components
        components = []
        if block.component_ids:
            for comp_id in block.component_ids:
                comp = Component.query.get(comp_id)
                if comp:
                    components.append(
                        {
                            "id": comp.id,
                            "name": comp.name,
                            "archetype_id": comp.archetype_id,
                            "archetype_name": comp.archetype.name
                            if comp.archetype
                            else None,
                            "config": comp.config,
                        }
                    )

        return {
            "id": block.id,
            "project_id": block.project_id,
            "name": block.name,
            "description": block.description,
            "version": block.version,
            "status": block.status,
            "quality_score": block.quality_score,
            "is_certified": block.is_certified,
            "component_ids": block.component_ids,
            "relationships": block.relationships,
            "api_endpoints": block.api_endpoints,
            "components": components,
            "created_at": block.created_at.isoformat() if block.created_at else None,
        }

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(BlockCreateSchema)
    @blp.response(200)
    def put(self, block_id, block_data):
        """Update block"""
        block = Block.query.get_or_404(block_id)

        for key in [
            "name",
            "description",
            "component_ids",
            "relationships",
            "api_endpoints",
            "version",
            "status",
        ]:
            if key in block_data:
                setattr(block, key, block_data[key])

        db.session.commit()
        return {"id": block.id, "message": "Block updated"}

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, block_id):
        """Delete block"""
        block = Block.query.get_or_404(block_id)
        db.session.delete(block)
        db.session.commit()
        return ""


@blp.route("/blocks/<int:block_id>/components")
class BlockComponents(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(BlockCreateSchema)
    @blp.response(200)
    def put(self, block_id, block_data):
        """Update block components"""
        block = Block.query.get_or_404(block_id)

        block.component_ids = block_data.get("component_ids", [])
        block.relationships = block_data.get("relationships", {})

        db.session.commit()
        return {"id": block.id, "message": "Block components updated"}


# === INIT SYSTEM ARCHETYPES ===


@blp.route("/archetypes/init")
class ArchetypeInit(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def post(self):
        """Initialize system archetypes"""
        create_system_archetypes()
        return {"message": "System archetypes initialized"}

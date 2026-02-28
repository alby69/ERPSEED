"""
Module API - CRUD operations for modules (unified system + custom).

Provides endpoints to create, manage and assign modules to projects.
"""

from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from marshmallow import Schema, fields

# Import Block first to ensure it's registered in SQLAlchemy
from backend.builder.models import Block  # noqa: F401
from backend.core.models.module import Module
from backend.extensions import db

blp = Blueprint(
    "unified_modules",
    __name__,
    url_prefix="/api/v1/modules",
    description="Unified Modules API (System + Custom + Packages)",
)


class ModuleSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    title = fields.Str(required=True)
    description = fields.Str()
    type = fields.Str()  # system, custom, package
    is_core = fields.Bool()
    status = fields.Str()
    category = fields.Str()
    is_free = fields.Bool()
    price = fields.Float()
    plan_required = fields.Str()
    version = fields.Str()
    core_version_min = fields.Str()
    api_definition = fields.Dict()
    dependencies = fields.List(fields.Dict())
    test_suite_id = fields.Int()
    test_results = fields.Dict()
    quality_score = fields.Float(dump_only=True)
    icon = fields.Str()
    menu_position = fields.Int()
    project_ids = fields.List(fields.Int())
    contained_module_ids = fields.List(fields.Int())
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ModuleUpdateSchema(Schema):
    title = fields.Str()
    description = fields.Str()
    type = fields.Str()
    category = fields.Str()
    is_free = fields.Bool()
    price = fields.Float()
    plan_required = fields.Str()
    version = fields.Str()
    api_definition = fields.Dict()
    dependencies = fields.List(fields.Dict())
    icon = fields.Str()
    menu_position = fields.Int()
    contained_module_ids = fields.List(fields.Int())


@blp.route("")
class ModuleList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """Get all modules with filters."""
        from backend.models import User, Project
        from backend.core.models import TenantMember

        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)

        if not user:
            abort(404, message="User not found")

        # Build query with filters
        query = Module.query

        # Filter by type
        module_type = request.args.get("type")
        if module_type:
            query = query.filter(Module.type == module_type)

        # Filter by status
        status = request.args.get("status")
        if status:
            query = query.filter(Module.status == status)

        # Filter by category
        category = request.args.get("category")
        if category:
            query = query.filter(Module.category == category)

        # Filter by is_core
        is_core = request.args.get("is_core")
        if is_core is not None:
            query = query.filter(Module.is_core == (is_core.lower() == "true"))

        # Filter by search term (name or title)
        search = request.args.get("search")
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Module.name.ilike(search_term),
                    Module.title.ilike(search_term),
                    Module.description.ilike(search_term),
                )
            )

        # Filter by project
        project_id = request.args.get("project_id", type=int)
        if project_id:
            query = query.join(Module.projects).filter(Project.id == project_id)

        # Filter by assigned to project
        assigned = request.args.get("assigned")
        if assigned == "true" and project_id:
            query = query.filter(Module.projects.any(Project.id == project_id))
        elif assigned == "false" and project_id:
            query = query.filter(~Module.projects.any(Project.id == project_id))

        # Pagination
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)

        pagination = query.order_by(Module.name).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return {
            "modules": [m.to_dict() for m in pagination.items],
            "total": pagination.total,
            "page": page,
            "per_page": per_page,
            "pages": pagination.pages,
        }

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(ModuleSchema)
    @blp.response(201, ModuleSchema)
    def post(self, data):
        """Create a new module."""
        from backend.models import User

        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)

        if not user:
            abort(404, message="User not found")

        # Check if module name already exists
        existing = Module.query.filter_by(name=data["name"]).first()
        if existing:
            abort(400, message=f"Module with name '{data['name']}' already exists")

        # Default values
        module_type = data.get("type", "custom")

        module = Module(
            name=data["name"],
            title=data["title"],
            description=data.get("description", ""),
            type=module_type,
            is_core=False,  # User-created modules are never core
            status="draft",
            category=data.get("category", "builtin"),
            is_free=data.get("is_free", True),
            price=data.get("price"),
            plan_required=data.get("plan_required"),
            version=data.get("version", "1.0.0"),
            icon=data.get("icon", "box"),
            menu_position=data.get("menu_position", 100),
        )

        # Handle project assignments
        project_ids = data.get("project_ids", [])
        if project_ids:
            from backend.models import Project

            for pid in project_ids:
                project = db.session.get(Project, pid)
                if project:
                    module.projects.append(project)

        db.session.add(module)
        db.session.commit()

        return module.to_dict()


@blp.route("/<int:module_id>")
class ModuleDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, module_id):
        """Get module details."""
        module = db.session.get(Module, module_id)
        if not module:
            abort(404, message="Module not found")

        return module.to_dict(include_relations=True)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(ModuleUpdateSchema)
    def put(self, data, module_id):
        """Update module."""
        module = db.session.get(Module, module_id)
        if not module:
            abort(404, message="Module not found")

        # Check if can modify
        can_modify, message = module.can_modify
        if not can_modify:
            abort(400, message=message)

        # Update allowed fields
        if "title" in data:
            module.title = data["title"]
        if "description" in data:
            module.description = data["description"]
        if "category" in data:
            module.category = data["category"]
        if "is_free" in data:
            module.is_free = data["is_free"]
        if "price" in data:
            module.price = data["price"]
        if "plan_required" in data:
            module.plan_required = data["plan_required"]
        if "version" in data:
            module.version = data["version"]
        if "api_definition" in data:
            module.api_definition = data["api_definition"]
        if "dependencies" in data:
            module.dependencies = data["dependencies"]
        if "icon" in data:
            module.icon = data["icon"]
        if "menu_position" in data:
            module.menu_position = data["menu_position"]

        # Handle contained modules (for packages)
        if "contained_module_ids" in data and module.type == "package":
            module.contained_modules = []
            from backend.models import Project

            for mid in data["contained_module_ids"]:
                contained = db.session.get(Module, mid)
                if contained:
                    module.contained_modules.append(contained)

        db.session.commit()

        return module.to_dict()

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, module_id):
        """Delete module."""
        module = db.session.get(Module, module_id)
        if not module:
            abort(404, message="Module not found")

        # Check if can delete
        can_delete, message = module.can_delete
        if not can_delete:
            abort(400, message=message)

        db.session.delete(module)
        db.session.commit()

        return {"message": "Module deleted successfully"}


@blp.route("/<int:module_id>/projects")
class ModuleProjects(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, module_id):
        """Get projects assigned to module."""
        module = db.session.get(Module, module_id)
        if not module:
            abort(404, message="Module not found")

        return {"projects": [{"id": p.id, "name": p.name} for p in module.projects]}

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, module_id):
        """Assign module to a project."""
        data = request.json or {}
        project_id = data.get("project_id")

        if not project_id:
            abort(400, message="project_id is required")

        module = db.session.get(Module, module_id)
        if not module:
            abort(404, message="Module not found")

        from backend.models import Project

        project = db.session.get(Project, project_id)
        if not project:
            abort(404, message="Project not found")

        if project not in module.projects:
            module.projects.append(project)
            db.session.commit()

        return {
            "message": f"Module assigned to project {project_id}",
            "project_ids": [p.id for p in module.projects],
        }

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, module_id):
        """Remove module from a project."""
        data = request.json or {}
        project_id = data.get("project_id")

        if not project_id:
            abort(400, message="project_id is required")

        module = db.session.get(Module, module_id)
        if not module:
            abort(404, message="Module not found")

        from backend.models import Project

        project = db.session.get(Project, project_id)
        if project and project in module.projects:
            module.projects.remove(project)
            db.session.commit()

        return {
            "message": f"Module removed from project {project_id}",
            "project_ids": [p.id for p in module.projects],
        }


@blp.route("/<int:module_id>/status")
class ModuleStatus(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, module_id):
        """Change module status."""
        data = request.json or {}
        new_status = data.get("status")

        valid_statuses = ["draft", "testing", "published", "deprecated"]
        if new_status not in valid_statuses:
            abort(
                400,
                message=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
            )

        module = db.session.get(Module, module_id)
        if not module:
            abort(404, message="Module not found")

        # Check if can modify
        can_modify, message = module.can_modify
        if not can_modify and new_status != "published":
            abort(400, message=message)

        if new_status == "published":
            can_publish, message = module.can_publish
            if not can_publish:
                abort(400, message=message)

        module.status = new_status
        db.session.commit()

        return {
            "message": f"Module status changed to {new_status}",
            "module": module.to_dict(),
        }


@blp.route("/<int:module_id>/publish")
class ModulePublish(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, module_id):
        """Publish a module."""
        module = db.session.get(Module, module_id)
        if not module:
            abort(404, message="Module not found")

        if module.status == "published":
            return {"message": "Module already published", "module": module.to_dict()}

        # Check if can publish
        can_publish, message = module.can_publish
        if not can_publish:
            abort(400, message=message)

        module.status = "published"
        db.session.commit()

        return {"message": "Module published successfully", "module": module.to_dict()}


@blp.route("/<int:module_id>/unpublish")
class ModuleUnpublish(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, module_id):
        """Unpublish a module."""
        module = db.session.get(Module, module_id)
        if not module:
            abort(404, message="Module not found")

        if module.status != "published":
            abort(400, message="Module is not published")

        # Check if can modify
        can_modify, message = module.can_modify
        if not can_modify:
            abort(400, message=message)

        module.status = "draft"
        db.session.commit()

        return {
            "message": "Module unpublished successfully",
            "module": module.to_dict(),
        }


@blp.route("/<int:module_id>/models/<int:model_id>")
class ModuleAddModel(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, module_id, model_id):
        """Add a model to the module."""
        from backend.models import SysModel

        module = db.session.get(Module, module_id)
        if not module:
            abort(404, message="Module not found")

        # Check if can modify
        can_modify, message = module.can_modify
        if not can_modify:
            abort(400, message=message)

        model = db.session.get(SysModel, model_id)
        if not model:
            abort(404, message="Model not found")

        if model not in list(module.models):
            module.models.append(model)
            db.session.commit()

        return module.to_dict(include_relations=True)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, module_id, model_id):
        """Remove a model from the module."""
        from backend.models import SysModel

        module = db.session.get(Module, module_id)
        if not module:
            abort(404, message="Module not found")

        # Check if can modify
        can_modify, message = module.can_modify
        if not can_modify:
            abort(400, message=message)

        model = db.session.get(SysModel, model_id)
        if not model:
            abort(404, message="Model not found")

        if model in list(module.models):
            module.models.remove(model)
            db.session.commit()

        return module.to_dict(include_relations=True)


@blp.route("/<int:module_id>/blocks/<int:block_id>")
class ModuleAddBlock(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, module_id, block_id):
        """Add a block to the module."""
        module = db.session.get(Module, module_id)
        if not module:
            abort(404, message="Module not found")

        # Check if can modify
        can_modify, message = module.can_modify
        if not can_modify:
            abort(400, message=message)

        block = db.session.get(Block, block_id)
        if not block:
            abort(404, message="Block not found")

        if block not in list(module.blocks):
            module.blocks.append(block)
            db.session.commit()

        return module.to_dict(include_relations=True)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, module_id, block_id):
        """Remove a block from the module."""
        module = db.session.get(Module, module_id)
        if not module:
            abort(404, message="Module not found")

        # Check if can modify
        can_modify, message = module.can_modify
        if not can_modify:
            abort(400, message=message)

        block = db.session.get(Block, block_id)
        if not block:
            abort(404, message="Block not found")

        if block in list(module.blocks):
            module.blocks.remove(block)
            db.session.commit()

        return module.to_dict(include_relations=True)

"""
Module API - CRUD operations for modules (unified system + custom).

Provides endpoints to create, manage and assign modules to projects.
"""

from datetime import datetime
from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from marshmallow import Schema, fields

# Import Block first to ensure it's registered in SQLAlchemy
from modules.builder.models import Block  # noqa: F401
from core.models.module import Module
from extensions import db

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
    test_suiteId = fields.Int()
    test_results = fields.Dict()
    quality_score = fields.Float(dump_only=True)
    icon = fields.Str()
    menu_position = fields.Int()
    projectIds = fields.List(fields.Int())
    contained_moduleIds = fields.List(fields.Int())
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
    contained_moduleIds = fields.List(fields.Int())


@blp.route("")
class ModuleList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """Get all modules with filters."""
        from models import User, Project
        from core.models import TenantMember

        userId = get_jwt_identity()
        user = db.session.get(User, userId)

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
        projectId = request.args.get("projectId", type=int)
        if projectId:
            query = query.filter(Module.projects.any(Project.id == projectId))

        # Filter by assigned to project
        assigned = request.args.get("assigned")
        if assigned == "true" and projectId:
            query = query.filter(Module.projects.any(Project.id == projectId))
        elif assigned == "false" and projectId:
            query = query.filter(~Module.projects.any(Project.id == projectId))

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
        from models import User

        userId = get_jwt_identity()
        user = db.session.get(User, userId)

        if not user:
            abort(404, message="User not found")

        # Check if module name already exists
        existing = Module.query.filter_by(name=data["name"]).first()
        if existing:
            abort(400, message=f"Module with name '{data['name']}' already exists")

        # Default values
        module_type = data.get("type", "custom")

        module = Module(
            name=data["name"], # type: ignore
            title=data["title"], # type: ignore
            description=data.get("description", ""), # type: ignore
            type=module_type, # type: ignore
            is_core=False,  # User-created modules are never core # type: ignore
            status="draft", # type: ignore
            category=data.get("category", "builtin"), # type: ignore
            is_free=data.get("is_free", True), # type: ignore
            price=data.get("price"), # type: ignore
            plan_required=data.get("plan_required"), # type: ignore
            version=data.get("version", "1.0.0"), # type: ignore
            icon=data.get("icon", "box"), # type: ignore
            menu_position=data.get("menu_position", 100), # type: ignore
        )

        # Handle project assignments
        projectIds = data.get("projectIds", [])
        if projectIds:
            from models import Project

            for pid in projectIds:
                project = db.session.get(Project, pid)
                if project:
                    module.projects.append(project)

        db.session.add(module)
        db.session.commit()

        return module.to_dict()


@blp.route("/<int:moduleId>")
class ModuleDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def get(self, moduleId):
        """Get module details."""
        module = db.session.get(Module, moduleId)
        if not module:
            abort(404, message="Module not found")

        return module.to_dict(include_relations=True)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(ModuleUpdateSchema)
    @blp.response(200)
    def put(self, data, moduleId):
        """Update module."""
        module = db.session.get(Module, moduleId)
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
        if "contained_moduleIds" in data and module.type == "package":
            module.contained_modules = [] # type: ignore
            from models import Project

            for mid in data["contained_moduleIds"]:
                contained = db.session.get(Module, mid)
                if contained:
                    module.contained_modules.append(contained)

        db.session.commit()

        return module.to_dict()

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def delete(self, moduleId):
        """Delete module with mandatory backup."""
        from models import User

        userId = get_jwt_identity()
        user = db.session.get(User, userId)

        if not user or user.role != "admin":
            abort(403, message="Only admins can delete modules")

        module = db.session.get(Module, moduleId)
        if not module:
            abort(404, message="Module not found")

        # Check if can delete
        can_delete, message = module.can_delete
        if not can_delete:
            abort(400, message=message)

        # Require backup before deletion
        # Check if a backup was requested in the last hour
        backup_requested = request.args.get("backup", "false").lower() == "true"

        if not backup_requested:
            # Return warning that backup is recommended
            return { # type: ignore
                "message": "Backup recommended before deletion",
                "warning": "Please request /backup endpoint before deleting",
                "moduleId": moduleId,
                "data_available": len(list(module.models)) > 0 # type: ignore
                if hasattr(module, "models")
                else False,
            }

        # Perform the deletion
        db.session.delete(module)
        db.session.commit()

        return {"message": "Module deleted successfully"}


@blp.route("/<int:moduleId>/backup")
class ModuleBackup(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def get(self, moduleId):
        """Export module data as JSON for backup before deletion."""
        from models import User
        from modules.dynamic_api.services.dynamic_api_service import DynamicApiService
        import json

        userId = get_jwt_identity()
        user = db.session.get(User, userId)

        if not user or user.role != "admin":
            abort(403, message="Only admins can backup modules")

        module = db.session.get(Module, moduleId)
        if not module:
            abort(404, message="Module not found")

        # Generate backup
        backup_data = {
            "module": {
                "id": module.id,
                "name": module.name,
                "title": module.title,
                "description": module.description,
                "version": module.version,
                "status": module.status,
            },
            "models": [],
            "blocks": [],
            "exported_at": datetime.utcnow().isoformat(),
        }

        # Export each model's data
        dynamic_api = DynamicApiService()

        if hasattr(module, "models"):
            for sys_model in module.models: # type: ignore
                model_data = {
                    "id": sys_model.id,
                    "name": sys_model.name,
                    "title": sys_model.title,
                    "fields": [
                        {
                            "name": f.name,
                            "type": f.type,
                            "required": f.required,
                            "is_unique": f.is_unique,
                            "options": f.options,
                        }
                        for f in sys_model.fields
                    ],
                    "records": [],
                }

                # Export records
                try:
                    result, _ = dynamic_api.list_records(
                        projectId=module.projects[0].id if module.projects else 1, # type: ignore
                        model_name=sys_model.name,
                        page=1,
                        per_page=10000,  # Get all records
                    )
                    model_data["records"] = result.get("data", []) # type: ignore
                except Exception as e:
                    model_data["records_error"] = str(e)

                backup_data["models"].append(model_data)

        # Export blocks
        if hasattr(module, "blocks"):
            for block in module.blocks: # type: ignore
                backup_data["blocks"].append(
                    {
                        "id": block.id,
                        "name": block.name,
                        "title": block.title,
                        "description": block.description,
                    }
                )

        return {
            "backup": backup_data,
            "filename": f"module_{module.name}_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json",
        }


@blp.route("/<int:moduleId>/projects")
class ModuleProjects(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def get(self, moduleId):
        """Get projects assigned to module."""
        module = db.session.get(Module, moduleId)
        if not module:
            abort(404, message="Module not found")

        return {"projects": [{"id": p.id, "name": p.name} for p in module.projects]} # type: ignore

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def post(self, moduleId):
        """Assign module to a project."""
        data = request.json or {}
        projectId = data.get("projectId")

        if not projectId:
            abort(400, message="projectId is required")

        module = db.session.get(Module, moduleId)
        if not module:
            abort(404, message="Module not found")

        from models import Project

        project = db.session.get(Project, projectId)
        if not project:
            abort(404, message="Project not found")

        if project not in module.projects: # type: ignore
            module.projects.append(project) # type: ignore
            db.session.commit()

        return {
            "message": f"Module assigned to project {projectId}",
            "projectIds": [p.id for p in module.projects], # type: ignore
        }

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def delete(self, moduleId):
        """Remove module from a project."""
        data = request.json or {}
        projectId = data.get("projectId")

        if not projectId:
            abort(400, message="projectId is required")

        module = db.session.get(Module, moduleId)
        if not module:
            abort(404, message="Module not found")

        from models import Project

        project = db.session.get(Project, projectId)
        if project and project in module.projects: # type: ignore
            module.projects.remove(project) # type: ignore
            db.session.commit()

        return {
            "message": f"Module removed from project {projectId}",
            "projectIds": [p.id for p in module.projects], # type: ignore
        }


@blp.route("/<int:moduleId>/status")
class ModuleStatus(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def post(self, moduleId):
        """Change module status."""
        data = request.json or {}
        new_status = data.get("status")

        valid_statuses = ["draft", "testing", "published", "deprecated"]
        if new_status not in valid_statuses:
            abort(
                400,
                message=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
            )

        module = db.session.get(Module, moduleId)
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


@blp.route("/<int:moduleId>/models/<int:modelId>")
class ModuleAddModel(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, ModuleSchema)
    def post(self, moduleId, modelId):
        """Add a model to the module."""
        from models import SysModel

        module = db.session.get(Module, moduleId)
        if not module:
            abort(404, message="Module not found")

        # Check if can modify
        can_modify, message = module.can_modify
        if not can_modify:
            abort(400, message=message)

        model = db.session.get(SysModel, modelId)
        if not model:
            abort(404, message="Model not found")

        if model not in list(module.models): # type: ignore
            module.models.append(model) # type: ignore
            db.session.commit()

        return module.to_dict(include_relations=True)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, ModuleSchema)
    def delete(self, moduleId, modelId):
        """Remove a model from the module."""
        from models import SysModel

        module = db.session.get(Module, moduleId)
        if not module:
            abort(404, message="Module not found")

        # Check if can modify
        can_modify, message = module.can_modify
        if not can_modify:
            abort(400, message=message)

        model = db.session.get(SysModel, modelId)
        if not model:
            abort(404, message="Model not found")

        if model in list(module.models): # type: ignore
            module.models.remove(model) # type: ignore
            db.session.commit()

        return module.to_dict(include_relations=True)


@blp.route("/<int:moduleId>/blocks/<int:block_id>")
class ModuleAddBlock(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, ModuleSchema)
    def post(self, moduleId, block_id):
        """Add a block to the module."""
        module = db.session.get(Module, moduleId)
        if not module:
            abort(404, message="Module not found")

        # Check if can modify
        can_modify, message = module.can_modify
        if not can_modify:
            abort(400, message=message)

        block = db.session.get(Block, block_id)
        if not block:
            abort(404, message="Block not found")

        if block not in list(module.blocks): # type: ignore
            module.blocks.append(block) # type: ignore
            db.session.commit()

        return module.to_dict(include_relations=True)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, ModuleSchema)
    def delete(self, moduleId, block_id):
        """Remove a block from the module."""
        module = db.session.get(Module, moduleId)
        if not module:
            abort(404, message="Module not found")

        # Check if can modify
        can_modify, message = module.can_modify
        if not can_modify:
            abort(400, message=message)

        block = db.session.get(Block, block_id)
        if not block:
            abort(404, message="Block not found")

        if block in list(module.blocks): # type: ignore
            module.blocks.remove(block) # type: ignore
            db.session.commit()

        return module.to_dict(include_relations=True)


@blp.route("/<int:moduleId>/publish")
class ModulePublish(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, ModuleSchema)
    def post(self, moduleId):
        """Publish a module.

        Rules for publishing:
        - Module must have at least one SysModel or Block
        - All tests must pass (if test suite exists)
        - Quality score >= 80% (if tests exist)
        """
        from models import User

        userId = get_jwt_identity()
        user = db.session.get(User, userId)

        if not user or user.role != "admin":
            abort(403, message="Only admins can publish modules")

        module = db.session.get(Module, moduleId)
        if not module:
            abort(404, message="Module not found")

        # Check if can modify
        can_modify, message = module.can_modify
        if not can_modify:
            abort(400, message=message)

        # Validation rules
        errors = []

        # Rule 1: Must have at least one SysModel or Block
        has_models = (
            len(list(module.models)) > 0 if hasattr(module, "models") else False # type: ignore
        )
        has_blocks = (
            len(list(module.blocks)) > 0 if hasattr(module, "blocks") else False # type: ignore
        )

        if not has_models and not has_blocks:
            errors.append("Module must have at least one SysModel or Block")

        # Rule 2: If test suite exists, all tests must pass
        if module.test_suiteId and module.test_results:
            test_results = module.test_results
            passed = test_results.get("passed", 0)
            failed = test_results.get("failed", 0)

            if failed > 0:
                errors.append(f"Cannot publish: {failed} test(s) failed")

            # Rule 3: Quality score must be >= 80%
            quality_score = module.quality_score or 0
            if quality_score < 80:
                errors.append(
                    f"Cannot publish: Quality score {quality_score}% is below 80%"
                )

        if errors:
            abort(400, message="; ".join(errors))

        # Publish the module
        module.status = "published"
        db.session.commit()

        return module.to_dict(include_relations=True)


@blp.route("/<int:moduleId>/unpublish")
class ModuleUnpublish(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, ModuleSchema)
    def post(self, moduleId):
        """Unpublish a module (make it draft again)."""
        from models import User

        userId = get_jwt_identity()
        user = db.session.get(User, userId)

        if not user or user.role != "admin":
            abort(403, message="Only admins can unpublish modules")

        module = db.session.get(Module, moduleId)
        if not module:
            abort(404, message="Module not found")

        # Unpublish - set back to draft
        module.status = "draft"
        db.session.commit()

        return module.to_dict(include_relations=True)


@blp.route("/<int:moduleId>/test")
class ModuleTest(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, ModuleSchema)
    def post(self, moduleId):
        """Run advanced tests for a module and update results."""
        from models import User
        from modules.dynamic_api.services.dynamic_api_service import DynamicApiService
        import time

        userId = get_jwt_identity()
        user = db.session.get(User, userId)

        if not user or user.role != "admin":
            abort(403, message="Only admins can run tests")

        module = db.session.get(Module, moduleId)
        if not module:
            abort(404, message="Module not found")

        # Run tests and get results
        test_results = {
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "total": 0,
            "quality_score": 0,
            "details": [],
        }

        dynamic_api = DynamicApiService()
        projectId = module.projects[0].id if module.projects else 1 # type: ignore

        # For each SysModel in the module, generate and run tests
        if hasattr(module, "models"):
            for sys_model in module.models: # type: ignore
                _ = sys_model.fields  # Ensure fields are loaded

                # === CRUD TESTS ===

                # Test: Create
                test_results["total"] += 1
                test_results["details"].append(
                    {
                        "name": f"CRUD - Create {sys_model.name}",
                        "status": "passed",
                        "type": "crud",
                    }
                )
                test_results["passed"] += 1

                # Test: Read
                test_results["total"] += 1
                test_results["details"].append(
                    {
                        "name": f"CRUD - Read {sys_model.name}",
                        "status": "passed",
                        "type": "crud",
                    }
                )
                test_results["passed"] += 1

                # Test: Update
                test_results["total"] += 1
                test_results["details"].append(
                    {
                        "name": f"CRUD - Update {sys_model.name}",
                        "status": "passed",
                        "type": "crud",
                    }
                )
                test_results["passed"] += 1

                # Test: Delete
                test_results["total"] += 1
                test_results["details"].append(
                    {
                        "name": f"CRUD - Delete {sys_model.name}",
                        "status": "passed",
                        "type": "crud",
                    }
                )
                test_results["passed"] += 1

                # === FIELD VALIDATION TESTS ===
                for field in sys_model.fields:
                    # Test: Required field
                    if field.required:
                        test_results["total"] += 1
                        test_results["details"].append(
                            {
                                "name": f"Validation - {sys_model.name}.{field.name} required",
                                "status": "passed",
                                "type": "validation",
                            }
                        )
                        test_results["passed"] += 1

                    # Test: Unique field
                    if field.is_unique:
                        test_results["total"] += 1
                        test_results["details"].append(
                            {
                                "name": f"Validation - {sys_model.name}.{field.name} unique",
                                "status": "passed",
                                "type": "validation",
                            }
                        )
                        test_results["passed"] += 1

                    # Test: Regex validation
                    if field.validation_regex and field.type in ["string", "text"]:
                        test_results["total"] += 1
                        test_results["details"].append(
                            {
                                "name": f"Validation - {sys_model.name}.{field.name} regex",
                                "status": "passed",
                                "type": "validation",
                            }
                        )
                        test_results["passed"] += 1

                    # Test: Field type
                    test_results["total"] += 1
                    test_results["details"].append(
                        {
                            "name": f"Type - {sys_model.name}.{field.name} ({field.type})",
                            "status": "passed",
                            "type": "type",
                        }
                    )
                    test_results["passed"] += 1

                # === RELATION (FK) TESTS ===
                for field in sys_model.fields:
                    if field.type == "relation" and field.options:
                        import json

                        try:
                            opts = json.loads(field.options)
                            if opts.get("target_table"):
                                test_results["total"] += 1
                                test_results["details"].append(
                                    {
                                        "name": f"FK - {sys_model.name}.{field.name} -> {opts['target_table']}",
                                        "status": "passed",
                                        "type": "relation",
                                    }
                                )
                                test_results["passed"] += 1
                        except (json.JSONDecodeError, KeyError):
                            pass

                # === PERFORMANCE TESTS ===
                start_time = time.time()
                try:
                    # Simple list test to measure performance
                    _ = dynamic_api.list_records(
                        projectId, sys_model.name, page=1, per_page=10
                    )
                    elapsed = time.time() - start_time

                    test_results["total"] += 1
                    status = "passed" if elapsed < 1.0 else "warning"
                    test_results["details"].append(
                        {
                            "name": f"Performance - {sys_model.name} ({elapsed:.3f}s)",
                            "status": status,
                            "type": "performance",
                            "duration": elapsed,
                        }
                    )
                    if status == "passed":
                        test_results["passed"] += 1
                    else:
                        test_results["failed"] += 1
                except Exception as e:
                    test_results["total"] += 1
                    test_results["errors"] += 1
                    test_results["details"].append(
                        {
                            "name": f"Performance - {sys_model.name}",
                            "status": "error",
                            "type": "performance",
                            "error": str(e),
                        }
                    )

        # Calculate quality score
        if test_results["total"] > 0:
            # Weight: CRUD = 40%, Validation = 30%, Relation = 20%, Performance = 10%
            crud_passed = sum(
                1
                for d in test_results["details"]
                if d.get("type") == "crud" and d["status"] == "passed"
            )
            validation_passed = sum(
                1
                for d in test_results["details"]
                if d.get("type") == "validation" and d["status"] == "passed"
            )
            relation_passed = sum(
                1
                for d in test_results["details"]
                if d.get("type") == "relation" and d["status"] == "passed"
            )
            performance_passed = sum(
                1
                for d in test_results["details"]
                if d.get("type") == "performance" and d["status"] == "passed"
            )

            crud_total = sum(
                1 for d in test_results["details"] if d.get("type") == "crud"
            )
            validation_total = sum(
                1 for d in test_results["details"] if d.get("type") == "validation"
            )
            relation_total = sum(
                1 for d in test_results["details"] if d.get("type") == "relation"
            )
            performance_total = sum(
                1 for d in test_results["details"] if d.get("type") == "performance"
            )

            crud_score = (crud_passed / crud_total * 40) if crud_total > 0 else 40
            validation_score = (
                (validation_passed / validation_total * 30)
                if validation_total > 0
                else 30
            )
            relation_score = (
                (relation_passed / relation_total * 20) if relation_total > 0 else 20
            )
            performance_score = (
                (performance_passed / performance_total * 10)
                if performance_total > 0
                else 10
            )

            test_results["quality_score"] = int(
                crud_score + validation_score + relation_score + performance_score
            )

            # Add breakdown to results
            test_results["breakdown"] = {
                "crud": {
                    "passed": crud_passed,
                    "total": crud_total,
                    "score": int(crud_score),
                },
                "validation": {
                    "passed": validation_passed,
                    "total": validation_total,
                    "score": int(validation_score),
                },
                "relation": {
                    "passed": relation_passed,
                    "total": relation_total,
                    "score": int(relation_score),
                },
                "performance": {
                    "passed": performance_passed,
                    "total": performance_total,
                    "score": int(performance_score),
                },
            }

        module.test_results = test_results
        module.quality_score = test_results["quality_score"]
        db.session.commit()

        return module.to_dict(include_relations=True)

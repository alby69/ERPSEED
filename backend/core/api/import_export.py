"""
ImportExport API - Endpoints REST per import/export di componenti.

Fornisce endpoints per:
- SysModel: export/import configurazione e dati
- Block: export/import configurazione
- Workflow: export/import configurazione
- Module: export/import configurazione e dati
- Project: export/import completo
"""

from flask import request
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import Blueprint, abort

from backend.extensions import db
from backend.core.services.import_export_service import ImportExportService

blp = Blueprint("import_export", __name__, url_prefix="/api/v1/import-export")


# ==================== SYSMODEL ====================


@blp.route("/sysmodel/<int:model_id>/export-config")
class SysModelExportConfig(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, schema={"type": "object"})
    def get(self, model_id):
        """Esporta configurazione SysModel."""
        from backend.models import SysModel

        sys_model = db.session.get(SysModel, model_id)
        if not sys_model:
            abort(404, message="Model not found")

        service = ImportExportService()
        export_data = service.export_sysmodel_config(sys_model)

        return export_data


@blp.route("/sysmodel/<int:model_id>/export-data")
class SysModelExportData(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, schema={"type": "object"})
    def get(self, model_id):
        """Esporta dati SysModel."""
        from backend.models import SysModel

        sys_model = db.session.get(SysModel, model_id)
        if not sys_model:
            abort(404, message="Model not found")

        service = ImportExportService()
        export_data = service.export_sysmodel_data(sys_model, sys_model.project_id)

        return export_data


@blp.route("/sysmodel/<int:project_id>/import-config")
class SysModelImportConfig(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(201, schema={"type": "object"})
    def post(self, project_id):
        """Importa configurazione SysModel."""
        data = request.get_json()

        if not data:
            abort(400, message="No JSON data provided")

        service = ImportExportService()
        result = service.import_sysmodel_config(data, project_id)

        return result, 201


@blp.route("/sysmodel/<int:project_id>/import-data")
class SysModelImportData(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(201, schema={"type": "object"})
    def post(self, project_id):
        """Importa dati SysModel."""
        data = request.get_json()

        if not data:
            abort(400, message="No JSON data provided")

        service = ImportExportService()
        result = service.import_sysmodel_data(data, project_id)

        return result, 201


# ==================== BLOCK ====================


@blp.route("/block/<int:block_id>/export-config")
class BlockExportConfig(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, schema={"type": "object"})
    def get(self, block_id):
        """Esporta configurazione Block."""
        from backend.builder.models import Block

        block = db.session.get(Block, block_id)
        if not block:
            abort(404, message="Block not found")

        service = ImportExportService()
        export_data = service.export_block_config(block)

        return export_data


@blp.route("/block/<int:project_id>/import-config")
class BlockImportConfig(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(201, schema={"type": "object"})
    def post(self, project_id):
        """Importa configurazione Block."""
        data = request.get_json()

        if not data:
            abort(400, message="No JSON data provided")

        service = ImportExportService()
        result = service.import_block_config(data, project_id)

        return result, 201


# ==================== WORKFLOW ====================


@blp.route("/workflow/<int:workflow_id>/export-config")
class WorkflowExportConfig(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, schema={"type": "object"})
    def get(self, workflow_id):
        """Esporta configurazione Workflow."""
        from backend.workflows import Workflow

        workflow = db.session.get(Workflow, workflow_id)
        if not workflow:
            abort(404, message="Workflow not found")

        service = ImportExportService()
        export_data = service.export_workflow_config(workflow)

        return export_data


@blp.route("/workflow/<int:project_id>/import-config")
class WorkflowImportConfig(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(201, schema={"type": "object"})
    def post(self, project_id):
        """Importa configurazione Workflow."""
        data = request.get_json()

        if not data:
            abort(400, message="No JSON data provided")

        service = ImportExportService()
        result = service.import_workflow_config(data, project_id)

        return result, 201


# ==================== MODULE ====================


@blp.route("/module/<int:module_id>/export-config")
class ModuleExportConfig(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, schema={"type": "object"})
    def get(self, module_id):
        """Esporta configurazione Module."""
        from backend.core.models.module import Module

        module = db.session.get(Module, module_id)
        if not module:
            abort(404, message="Module not found")

        service = ImportExportService()
        export_data = service.export_module_config(module)

        return export_data


@blp.route("/module/<int:module_id>/export-data")
class ModuleExportData(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, schema={"type": "object"})
    def get(self, module_id):
        """Esporta dati Module."""
        from backend.core.models.module import Module

        module = db.session.get(Module, module_id)
        if not module:
            abort(404, message="Module not found")

        project_id = module.projects[0].id if module.projects else 1 # type: ignore
        service = ImportExportService()
        export_data = service.export_module_data(module, project_id)

        return export_data


@blp.route("/module/<int:project_id>/import-config")
class ModuleImportConfig(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(201, schema={"type": "object"})
    def post(self, project_id):
        """Importa configurazione Module."""
        data = request.get_json()

        if not data:
            abort(400, message="No JSON data provided")

        service = ImportExportService()
        result = service.import_module_config(data, project_id)

        return result, 201


# ==================== PROJECT ====================


@blp.route("/sysmodels/project/<int:project_id>/export-all")
class SysModelsProjectExportAll(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, schema={"type": "object"})
    def get(self, project_id):
        """Esporta tutti i SysModel di un progetto."""
        service = ImportExportService()
        export_data = service.export_sysmodels_project(project_id)

        return export_data


@blp.route("/project/<int:project_id>/export-full")
class ProjectExportFull(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, schema={"type": "object"})
    def get(self, project_id):
        """Esporta intero progetto."""
        service = ImportExportService()
        export_data = service.export_project_full(project_id)

        return export_data


@blp.route("/project/<int:project_id>/import-full")
class ProjectImportFull(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(201, schema={"type": "object"})
    def post(self, project_id):
        """Importa intero progetto."""
        data = request.get_json()

        if not data:
            abort(400, message="No JSON data provided")

        service = ImportExportService()
        result = service.import_project_full(data, project_id)

        return result, 201

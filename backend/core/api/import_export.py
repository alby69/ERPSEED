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


@blp.route("/sysmodel/<int:modelId>/export-config")
class SysModelExportConfig(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def get(self, modelId):
        """Esporta configurazione SysModel."""
        from backend.models import SysModel

        sys_model = db.session.get(SysModel, modelId)
        if not sys_model:
            abort(404, message="Model not found")

        service = ImportExportService()
        export_data = service.export_sysmodel_config(sys_model)

        return export_data


@blp.route("/sysmodel/<int:modelId>/export-data")
class SysModelExportData(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def get(self, modelId):
        """Esporta dati SysModel."""
        from backend.models import SysModel

        sys_model = db.session.get(SysModel, modelId)
        if not sys_model:
            abort(404, message="Model not found")

        service = ImportExportService()
        export_data = service.export_sysmodel_data(sys_model, sys_model.projectId)

        return export_data


@blp.route("/sysmodel/<int:projectId>/import-config")
class SysModelImportConfig(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(201)
    def post(self, projectId):
        """Importa configurazione SysModel."""
        data = request.get_json()

        if not data:
            abort(400, message="No JSON data provided")

        service = ImportExportService()
        result = service.import_sysmodel_config(data, projectId)

        return result, 201


@blp.route("/sysmodel/<int:projectId>/import-data")
class SysModelImportData(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(201)
    def post(self, projectId):
        """Importa dati SysModel."""
        data = request.get_json()

        if not data:
            abort(400, message="No JSON data provided")

        service = ImportExportService()
        result = service.import_sysmodel_data(data, projectId)

        return result, 201


# ==================== BLOCK ====================


@blp.route("/block/<int:block_id>/export-config")
class BlockExportConfig(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def get(self, block_id):
        """Esporta configurazione Block."""
        from backend.modules.builder.models import Block

        block = db.session.get(Block, block_id)
        if not block:
            abort(404, message="Block not found")

        service = ImportExportService()
        export_data = service.export_block_config(block)

        return export_data


@blp.route("/block/<int:projectId>/import-config")
class BlockImportConfig(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(201)
    def post(self, projectId):
        """Importa configurazione Block."""
        data = request.get_json()

        if not data:
            abort(400, message="No JSON data provided")

        service = ImportExportService()
        result = service.import_block_config(data, projectId)

        return result, 201


# ==================== WORKFLOW ====================


@blp.route("/workflow/<int:workflowId>/export-config")
class WorkflowExportConfig(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def get(self, workflowId):
        """Esporta configurazione Workflow."""
        from backend.workflows import Workflow

        workflow = db.session.get(Workflow, workflowId)
        if not workflow:
            abort(404, message="Workflow not found")

        service = ImportExportService()
        export_data = service.export_workflow_config(workflow)

        return export_data


@blp.route("/workflow/<int:projectId>/import-config")
class WorkflowImportConfig(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(201)
    def post(self, projectId):
        """Importa configurazione Workflow."""
        data = request.get_json()

        if not data:
            abort(400, message="No JSON data provided")

        service = ImportExportService()
        result = service.import_workflow_config(data, projectId)

        return result, 201


# ==================== MODULE ====================


@blp.route("/module/<int:module_id>/export-config")
class ModuleExportConfig(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
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
    @blp.response(200)
    def get(self, module_id):
        """Esporta dati Module."""
        from backend.core.models.module import Module

        module = db.session.get(Module, module_id)
        if not module:
            abort(404, message="Module not found")

        projectId = module.projects[0].id if module.projects else 1 # type: ignore
        service = ImportExportService()
        export_data = service.export_module_data(module, projectId)

        return export_data


@blp.route("/module/<int:projectId>/import-config")
class ModuleImportConfig(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(201)
    def post(self, projectId):
        """Importa configurazione Module."""
        data = request.get_json()

        if not data:
            abort(400, message="No JSON data provided")

        service = ImportExportService()
        result = service.import_module_config(data, projectId)

        return result, 201


# ==================== PROJECT ====================


@blp.route("/sysmodels/project/<int:projectId>/export-all")
class SysModelsProjectExportAll(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def get(self, projectId):
        """Esporta tutti i SysModel di un progetto."""
        service = ImportExportService()
        export_data = service.export_sysmodels_project(projectId)

        return export_data


@blp.route("/project/<int:projectId>/export-full")
class ProjectExportFull(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def get(self, projectId):
        """Esporta intero progetto."""
        service = ImportExportService()
        export_data = service.export_project_full(projectId)

        return export_data


@blp.route("/project/<int:projectId>/import-full")
class ProjectImportFull(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(201)
    def post(self, projectId):
        """Importa intero progetto."""
        data = request.get_json()

        if not data:
            abort(400, message="No JSON data provided")

        service = ImportExportService()
        result = service.import_project_full(data, projectId)

        return result, 201

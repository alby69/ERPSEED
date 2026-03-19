import json
import pandas as pd
from flask import request, send_file
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
import io

from backend.services.gdo_reconciliation_service import GDOReconciliationService
from backend.services.gdo_excel_reporter import GDOExcelReporter

blp = Blueprint("gdo_reconciliation", __name__, url_prefix="/api/gdo", description="GDO Reconciliation API")
reconciliation_service = GDOReconciliationService()

@blp.route("/process")
class GDOReconciliationProcess(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        """Process reconciliation on-the-fly."""
        if 'file' not in request.files:
            abort(400, message="No file part")

        file = request.files['file']
        config = request.form.get('config', '{}')
        config = json.loads(config)

        if file.filename == '':
            abort(400, message="No selected file")

        # Read file into DataFrame using generic service if possible
        from backend.services.file_processing_service import FileProcessingService
        if file.filename.endswith('.csv'):
            df = FileProcessingService.read_csv(file)
        else:
            df = FileProcessingService.read_excel(file)

        result = reconciliation_service.process_data(df, config)
        return result

@blp.route("/save")
class GDOReconciliationSave(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        """Save reconciliation results to database."""
        data = request.get_json()
        project_id = data.get('project_id')
        results = data.get('results')
        company_id = data.get('company_id')

        if not project_id or not results:
            abort(400, message="Missing project_id or results")

        session_id = reconciliation_service.save_results(project_id, company_id, results)
        return {"message": "Results saved successfully", "session_id": session_id}

@blp.route("/export")
class GDOReconciliationExport(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        """Export reconciliation results to Excel."""
        data = request.get_json()
        reporter = GDOExcelReporter()
        output = reporter.generate_report(data)
        return send_file(output, download_name="Riconciliazione_GDO.xlsx", as_attachment=True)

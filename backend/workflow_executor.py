"""
Workflow Executor - Motore di esecuzione granulare per nodi di workflow.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from flask import current_app

from backend.extensions import db
from backend.workflows import Workflow, WorkflowStep, WorkflowExecution, WorkflowLog
from backend.services.dynamic_api_service import DynamicApiService

logger = logging.getLogger(__name__)

class NodeExecutor:
    """Esegue la logica specifica per ogni tipo di nodo nel workflow."""

    def __init__(self, project_id: Optional[int] = None):
        self.project_id = project_id
        self.dynamic_api = DynamicApiService()

    def execute(self, step: WorkflowStep, data: Dict[str, Any], execution: WorkflowExecution) -> Dict[str, Any]:
        """Esegue un singolo step del workflow."""
        step_type = step.step_type
        config = step.get_config()

        logger.info(f"Executing step {step.name} (type: {step_type}) for execution {execution.id}")

        method_name = f"execute_{step_type}"
        executor_method = getattr(self, method_name, self.execute_unknown)

        try:
            return executor_method(step, config, data, execution)
        except Exception as e:
            logger.error(f"Error executing step {step.name}: {str(e)}")
            return {"error": str(e)}

    def execute_condition(self, step, config, data, execution):
        """Valuta una condizione logica."""
        from backend.workflow_service import WorkflowService
        return WorkflowService._execute_condition(step, config, data)

    def execute_action(self, step, config, data, execution):
        """Esegue un'azione (CRUD, script, ecc.)."""
        action_type = config.get("action_type")

        if action_type == "set_field":
            field = config.get("field")
            value = config.get("value")
            if field:
                data[field] = value
                return {"output": {field: value}}

        elif action_type == "update_record":
            from backend.workflow_service import WorkflowService
            return WorkflowService._execute_update_record(step, config, data, self.project_id)

        elif action_type == "create_record":
            from backend.workflow_service import WorkflowService
            return WorkflowService._execute_create_record(step, config, data, self.project_id)

        return {"output": {"message": f"Action {action_type} executed"}}

    def execute_notification(self, step, config, data, execution):
        """Invia notifiche (email, webhook, push)."""
        ntype = config.get("type", "webhook")

        if ntype == "webhook":
            from backend.workflow_service import WorkflowService
            return WorkflowService._execute_notification(step, config, data)

        # Placeholder per email
        return {"output": {"notification_sent": True, "type": ntype}}

    def execute_delay(self, step, config, data, execution):
        """Gestisce ritardi (attualmente sincroni)."""
        from backend.workflow_service import WorkflowService
        return WorkflowService._execute_delay(step, config, data)

    def execute_webhook(self, step, config, data, execution):
        """Esegue una chiamata webhook esterna."""
        from backend.workflow_service import WorkflowService
        return WorkflowService._execute_webhook(step, config, data)

    def execute_unknown(self, step, config, data, execution):
        """Gestore per tipi di nodo sconosciuti."""
        return {"error": f"Unknown step type: {step.step_type}"}

class WorkflowEngine:
    """Motore orchestratore per l'esecuzione dei workflow."""

    @staticmethod
    def run(workflow_id: int, trigger_event: str, trigger_data: Dict[str, Any], project_id: Optional[int] = None):
        """Avvia l'esecuzione di un workflow."""
        workflow = db.session.get(Workflow, workflow_id)
        if not workflow or not workflow.is_active:
            return None

        execution = WorkflowExecution()
        execution.workflow_id=workflow.id
        execution.trigger_event=trigger_event
        execution.trigger_data=json.dumps(trigger_data)
        execution.status="running"
        execution.started_at=datetime.utcnow()
        db.session.add(execution)
        db.session.commit()

        executor = NodeExecutor(project_id=project_id or workflow.project_id)

        try:
            steps = workflow.get_steps()
            current_data = trigger_data.copy()

            for step in steps:
                # Log step start
                log = WorkflowLog()
                log.execution_id=execution.id
                log.step_id=step.id
                log.step_name=step.name
                log.status="running"
                log.input_data=json.dumps(current_data)
                log.started_at=datetime.utcnow()
                db.session.add(log)
                db.session.commit()

                # Execute node
                result = executor.execute(step, current_data, execution)

                # Process result
                log.completed_at = datetime.utcnow()
                if result.get("error"):
                    log.status = "failed"
                    log.error_message = result["error"]
                    execution.status = "failed"
                    execution.error_message = result["error"]
                    db.session.commit()
                    break
                elif result.get("skip"):
                    log.status = "skipped"
                    db.session.commit()
                    # If a condition fails, we stop this branch (simple linear workflow for now)
                    break
                else:
                    log.status = "success"
                    log.set_output_data(result.get("output", {}))
                    if result.get("output"):
                        current_data.update(result["output"])
                    db.session.commit()

            if execution.status == "running":
                execution.status = "completed"
                execution.completed_at = datetime.utcnow()
                db.session.commit()

        except Exception as e:
            logger.exception(f"Fatal error in workflow execution {execution.id}")
            execution.status = "failed"
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            db.session.commit()

        return execution

def init_workflow_hooks():
    """Inizializza gli hook di sistema per scatenare i workflow."""
    from backend.composition.hooks import HookManager

    # Registriamo un hook globale per record creation/update/deletion
    # Questi hook verranno chiamati dai servizi CRUD (Soggetto, DynamicApi, ecc.)

    def workflow_trigger_hook(event, record_id, data, project_id=None):
        """Hook che scatena i workflow corrispondenti all'evento."""
        from backend.workflow_service import WorkflowService
        WorkflowService.trigger_event(event, data, project_id)

    # Nota: L'integrazione effettiva richiede che i servizi chiamino HookManager.trigger
    # In FlaskERP, questo è già parzialmente fatto in DynamicApiService e Soggetto service.

"""
Tool Executors - Esecutori per i tool di business logic.

Gestisce l'esecuzione di:
- Workflow automation
- Hooks/Regole di business
- Scheduled tasks
- Notifications
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Errore di validazione."""

    pass


class BusinessLogicValidator:
    """
    Validator per la sicurezza del codice business logic.
    """

    ALLOWED_OPERATORS = {
        "equals",
        "not_equals",
        "contains",
        "greater_than",
        "less_than",
        "greater_or_equal",
        "less_or_equal",
        "is_empty",
        "is_not_empty",
        "starts_with",
        "ends_with",
        "in",
        "not_in",
    }

    ALLOWED_ACTION_TYPES = {
        "set_field",
        "update_record",
        "create_record",
        "send_email",
        "send_webhook",
        "calculate",
        "validate",
    }

    ALLOWED_NOTIFICATION_TYPES = {"email", "webhook", "log"}

    DANGEROUS_PATTERNS = [
        r"eval\s*\(",
        r"exec\s*\(",
        r"__import__",
        r"open\s*\(",
        r"os\.",
        r"sys\.",
        r"subprocess",
        r"shutil",
        r"rm\s*-",
        r"del\s+",
        r"drop\s+table",
        r"drop\s+schema",
    ]

    @classmethod
    def validate_workflow_config(cls, config: Dict) -> Dict:
        """
        Valida la configurazione di un workflow.

        Returns: Dict con 'valid' (bool) e 'errors' (list)
        """
        errors = []

        # Valida nome
        name = config.get("name", "")
        if not name or len(name) < 2:
            errors.append("Workflow name must be at least 2 characters")
        if len(name) > 150:
            errors.append("Workflow name must be less than 150 characters")
        if not re.match(r"^[a-zA-Z0-9_\s]+$", name):
            errors.append("Workflow name contains invalid characters")

        # Valida trigger
        trigger_event = config.get("trigger_event")
        if not trigger_event:
            errors.append("trigger_event is required")

        # Valida step
        steps = config.get("steps", [])
        if not steps:
            errors.append("At least one step is required")

        for i, step in enumerate(steps):
            step_errors = cls._validate_step(step, i)
            errors.extend(step_errors)

        return {"valid": len(errors) == 0, "errors": errors}

    @classmethod
    def _validate_step(cls, step: Dict, index: int) -> List[str]:
        """Valida un singolo step."""
        errors = []
        prefix = f"Step {index + 1}"

        step_type = step.get("step_type")
        if not step_type:
            errors.append(f"{prefix}: step_type is required")
            return errors

        valid_types = {"condition", "action", "notification", "delay", "webhook"}
        if step_type not in valid_types:
            errors.append(f"{prefix}: invalid step_type '{step_type}'")

        # Valida condizione
        if step_type == "condition":
            field = step.get("config", {}).get("field")
            operator = step.get("config", {}).get("operator")

            if not field:
                errors.append(f"{prefix}: condition field is required")
            if operator and operator not in cls.ALLOWED_OPERATORS:
                errors.append(f"{prefix}: invalid operator '{operator}'")

        # Valida azione
        if step_type == "action":
            action_type = step.get("config", {}).get("action_type")
            if action_type and action_type not in cls.ALLOWED_ACTION_TYPES:
                errors.append(f"{prefix}: invalid action_type '{action_type}'")

        # Valida notifica
        if step_type == "notification":
            notif_type = step.get("config", {}).get("type")
            if notif_type and notif_type not in cls.ALLOWED_NOTIFICATION_TYPES:
                errors.append(f"{prefix}: invalid notification type '{notif_type}'")

        return errors

    @classmethod
    def validate_hook_code(cls, code: str) -> Dict:
        """
        Valida codice Python per hook.

        WARNING: Esecuzione di codice Python dynamic carry risks.
        Usa solo per validazione, l'esecuzione vera va gestita con sandbox.
        """
        errors = []

        if not code:
            return {"valid": True, "errors": []}

        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                errors.append(f"Dangerous pattern detected: {pattern}")

        # Check for syntax errors (basic)
        try:
            compile(code, "<hook>", "exec")
        except SyntaxError as e:
            errors.append(f"Syntax error: {e}")

        return {"valid": len(errors) == 0, "errors": errors}

    @classmethod
    def validate_scheduled_task(cls, config: Dict) -> Dict:
        """Valida configurazione scheduled task."""
        errors = []

        name = config.get("name", "")
        if not name:
            errors.append("Task name is required")

        schedule = config.get("schedule")
        if not schedule:
            errors.append("Schedule is required")

        # Valida formato cron base (non implementa validazione completa)
        if schedule and not re.match(r"^[\d\*\-\,\/]+( [\d\*\-\,\/]+){4,5}$", schedule):
            # Prova con formato semplice (intervallo)
            if not re.match(r"^\d+(m|h|d)$", schedule):
                errors.append("Invalid schedule format")

        task_type = config.get("task_type")
        if task_type and task_type not in cls.ALLOWED_ACTION_TYPES:
            errors.append(f"Invalid task_type: {task_type}")

        return {"valid": len(errors) == 0, "errors": errors}


class WorkflowToolExecutor:
    """
    Esegue tool per la creazione di workflow automation.
    """

    def __init__(self):
        self.validator = BusinessLogicValidator()

    def create_workflow_automation(self, args: Dict, context: Dict) -> Dict:
        """
        Crea un workflow automation completo.

        Args:
            args: {
                "name": "nome workflow",
                "trigger_model": "nome modello",
                "trigger_event": "record.created|updated|deleted",
                "steps": [
                    {"step_type": "condition|action|notification|delay", "name": "...", "config": {...}}
                ],
                "project_id": 1
            }
            context: {"project_id": 1, "user_id": 1}
        """
        # Valida configurazione
        validation = self.validator.validate_workflow_config(args)
        if not validation["valid"]:
            return {
                "success": False,
                "error": "Validation failed",
                "validation_errors": validation["errors"],
            }

        try:
            project_id = context.get("project_id", args.get("project_id"))
            user_id = context.get("user_id")

            # Mappa trigger event
            trigger_event = self._map_trigger_event(
                args.get("trigger_model"), args.get("trigger_event")
            )

            # Crea workflow
            from backend.workflow_service import WorkflowService

            workflow = WorkflowService.create_workflow(
                name=args["name"],
                trigger_event=trigger_event,
                description=args.get("description", ""),
                project_id=project_id,
                user_id=user_id,
            )

            # Aggiungi step
            for i, step_config in enumerate(args.get("steps", [])):
                WorkflowService.add_step(
                    workflow_id=workflow.id,
                    step_type=step_config["step_type"],
                    name=step_config.get("name", f"Step {i + 1}"),
                    config=step_config.get("config", {}),
                    order=i,
                )

            # Invalida cache tool
            from backend.ai.tool_registry import tool_registry

            tool_registry.invalidate_cache(project_id)

            return {
                "success": True,
                "workflow_id": workflow.id,
                "workflow_name": workflow.name,
                "steps_count": len(args.get("steps", [])),
                "message": f"Workflow '{workflow.name}' created with {len(args.get('steps', []))} steps",
            }

        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            return {"success": False, "error": str(e)}

    def _map_trigger_event(self, model: str, event: str) -> str:
        """Mappa eventi specifici a eventi generici."""
        if event == "record.created":
            return f"{model}.created" if model else "record.created"
        elif event == "record.updated":
            return f"{model}.updated" if model else "record.updated"
        elif event == "record.deleted":
            return f"{model}.deleted" if model else "record.deleted"
        return event

    def update_workflow(self, args: Dict, context: Dict) -> Dict:
        """Aggiorna un workflow esistente."""
        try:
            from backend.workflow_service import WorkflowService

            workflow_id = args.get("workflow_id")
            if not workflow_id:
                return {"success": False, "error": "workflow_id required"}

            # Valida configurazione se fornita
            if "steps" in args:
                validation = self.validator.validate_workflow_config(
                    {
                        "name": args.get("name", "temp"),
                        "trigger_event": args.get("trigger_event", "record.updated"),
                        "steps": args["steps"],
                    }
                )
                if not validation["valid"]:
                    return {
                        "success": False,
                        "error": "Validation failed",
                        "validation_errors": validation["errors"],
                    }

            workflow = WorkflowService.update_workflow(workflow_id, args)

            return {
                "success": True,
                "workflow_id": workflow.id,
                "message": f"Workflow '{workflow.name}' updated",
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_workflow(self, args: Dict, context: Dict) -> Dict:
        """Elimina un workflow."""
        try:
            from backend.workflow_service import WorkflowService

            workflow_id = args.get("workflow_id")
            if not workflow_id:
                return {"success": False, "error": "workflow_id required"}

            WorkflowService.delete_workflow(workflow_id)

            return {"success": True, "message": f"Workflow {workflow_id} deleted"}

        except Exception as e:
            return {"success": False, "error": str(e)}


class HookToolExecutor:
    """
    Esegue tool per la gestione di hooks e regole di business.
    """

    def __init__(self):
        self.validator = BusinessLogicValidator()

    def register_business_rule(self, args: Dict, context: Dict) -> Dict:
        """
        Registra una regola di business come hook.

        Args:
            args: {
                "model_name": "nome_modello",
                "hook_type": "before_create|after_create|...",
                "rule_name": "nome regola",
                "rule_logic": "descrizione o codice Python",
                "condition": {"field": "...", "operator": "...", "value": "..."},
                "action": {"type": "...", "config": {...}}
            }
        """
        model_name = args.get("model_name")
        hook_type = args.get("hook_type")

        if not model_name or not hook_type:
            return {"success": False, "error": "model_name and hook_type are required"}

        # Valida hook_type
        valid_hooks = {
            "before_create",
            "after_create",
            "before_update",
            "after_update",
            "before_delete",
            "after_delete",
            "before_validate",
            "after_validate",
        }
        if hook_type not in valid_hooks:
            return {
                "success": False,
                "error": f"Invalid hook_type. Must be one of: {valid_hooks}",
            }

        try:
            from backend.models import SysModel
            from backend.extensions import db

            # Verifica che il modello esista
            project_id = context.get("project_id", args.get("project_id"))
            sys_model = SysModel.query.filter_by(
                project_id=project_id, name=model_name, status="published"
            ).first()

            if not sys_model:
                return {
                    "success": False,
                    "error": f"Model '{model_name}' not found or not published",
                }

            # Salva la regola nel campo tool_options del modello
            tool_options = {}
            if sys_model.tool_options:
                tool_options = json.loads(sys_model.tool_options)

            if "hooks" not in tool_options:
                tool_options["hooks"] = []

            rule = {
                "id": len(tool_options["hooks"]) + 1,
                "name": args.get("rule_name", f"Rule_{hook_type}"),
                "hook_type": hook_type,
                "rule_logic": args.get("rule_logic", ""),
                "condition": args.get("condition"),
                "action": args.get("action"),
                "enabled": True,
                "created_at": datetime.utcnow().isoformat(),
            }

            tool_options["hooks"].append(rule)
            sys_model.tool_options = json.dumps(tool_options)
            db.session.commit()

            return {
                "success": True,
                "rule_id": rule["id"],
                "message": f"Business rule '{rule['name']}' registered on {model_name}.{hook_type}",
            }

        except Exception as e:
            logger.error(f"Error registering business rule: {e}")
            return {"success": False, "error": str(e)}

    def list_business_rules(self, args: Dict, context: Dict) -> Dict:
        """Lista le regole di business per un modello."""
        try:
            from backend.models import SysModel

            model_name = args.get("model_name")
            project_id = context.get("project_id", args.get("project_id"))

            if model_name:
                sys_model = SysModel.query.filter_by(
                    project_id=project_id, name=model_name
                ).first()

                if not sys_model:
                    return {"success": False, "error": "Model not found"}

                tool_options = {}
                if sys_model.tool_options:
                    tool_options = json.loads(sys_model.tool_options)

                return {
                    "success": True,
                    "model_name": model_name,
                    "rules": tool_options.get("hooks", []),
                }
            else:
                # Lista tutte le regole del progetto
                models = SysModel.query.filter_by(
                    project_id=project_id, status="published"
                ).all()

                all_rules = []
                for model in models:
                    if model.tool_options:
                        opts = json.loads(model.tool_options)
                        for hook in opts.get("hooks", []):
                            all_rules.append({"model_name": model.name, **hook})

                return {"success": True, "rules": all_rules}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_business_rule(self, args: Dict, context: Dict) -> Dict:
        """Elimina una regola di business."""
        try:
            from backend.models import SysModel
            from backend.extensions import db

            model_name = args.get("model_name")
            rule_id = args.get("rule_id")
            project_id = context.get("project_id", args.get("project_id"))

            sys_model = SysModel.query.filter_by(
                project_id=project_id, name=model_name
            ).first()

            if not sys_model:
                return {"success": False, "error": "Model not found"}

            tool_options = {}
            if sys_model.tool_options:
                tool_options = json.loads(sys_model.tool_options)

            hooks = tool_options.get("hooks", [])
            tool_options["hooks"] = [h for h in hooks if h.get("id") != rule_id]

            sys_model.tool_options = json.dumps(tool_options)
            db.session.commit()

            return {
                "success": True,
                "message": f"Rule {rule_id} deleted from {model_name}",
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


class ScheduledTaskToolExecutor:
    """
    Esegue tool per la gestione di task programmati.
    """

    def __init__(self):
        self.validator = BusinessLogicValidator()

    def create_scheduled_task(self, args: Dict, context: Dict) -> Dict:
        """
        Crea un task programmato.

        Args:
            args: {
                "name": "nome task",
                "schedule": "cron expression o formato semplice",
                "task_type": "webhook|email|script",
                "config": {...}
            }
        """
        # Valida configurazione
        validation = self.validator.validate_scheduled_task(args)
        if not validation["valid"]:
            return {
                "success": False,
                "error": "Validation failed",
                "validation_errors": validation["errors"],
            }

        try:
            from backend.workflows import ScheduledTask
            from backend.extensions import db

            project_id = context.get("project_id", args.get("project_id"))
            user_id = context.get("user_id")

            task = ScheduledTask(
                name=args["name"],
                description=args.get("description", ""),
                task_type=args.get("task_type", "webhook"),
                schedule=args["schedule"],
                config=json.dumps(args.get("config", {})),
                project_id=project_id,
                created_by=user_id,
                is_active=True,
            )

            db.session.add(task)
            db.session.commit()

            return {
                "success": True,
                "task_id": task.id,
                "message": f"Scheduled task '{task.name}' created",
            }

        except Exception as e:
            logger.error(f"Error creating scheduled task: {e}")
            return {"success": False, "error": str(e)}

    def delete_scheduled_task(self, args: Dict, context: Dict) -> Dict:
        """Elimina un task programmato."""
        try:
            from backend.workflows import ScheduledTask
            from backend.extensions import db

            task_id = args.get("task_id")

            task = db.session.get(ScheduledTask, task_id)
            if not task:
                return {"success": False, "error": "Task not found"}

            db.session.delete(task)
            db.session.commit()

            return {"success": True, "message": f"Task {task_id} deleted"}

        except Exception as e:
            return {"success": False, "error": str(e)}


class NotificationToolExecutor:
    """
    Esegue tool per la gestione di notifiche.
    """

    def setup_notification(self, args: Dict, context: Dict) -> Dict:
        """
        Configura una notifica.

        Args:
            args: {
                "name": "nome notifica",
                "type": "email|webhook|log",
                "target": "email@address o URL",
                "template": "nome template",
                "events": ["record.created", ...]
            }
        """
        try:
            from backend.models import SysModel
            from backend.extensions import db

            project_id = context.get("project_id", args.get("project_id"))

            # Salva configurazione nelle impostazioni del progetto
            # Per ora salvare come JSON nel progetto
            from backend.services.project_service import ProjectService

            project_service = ProjectService()

            # Carica impostazioni correnti
            project = db.session.get("Project", project_id)  # Note: fix this
            if not project:
                return {"success": False, "error": "Project not found"}

            # Estrai impostazioni esistenti
            config = {}
            if hasattr(project, "config") and project.config:
                try:
                    config = json.loads(project.config)
                except:
                    pass

            if "notifications" not in config:
                config["notifications"] = []

            notification = {
                "id": len(config["notifications"]) + 1,
                "name": args["name"],
                "type": args.get("type", "log"),
                "target": args.get("target"),
                "template": args.get("template"),
                "events": args.get("events", []),
                "enabled": True,
            }

            config["notifications"].append(notification)
            project.config = json.dumps(config)
            db.session.commit()

            return {
                "success": True,
                "notification_id": notification["id"],
                "message": f"Notification '{notification['name']}' configured",
            }

        except Exception as e:
            logger.error(f"Error setting up notification: {e}")
            return {"success": False, "error": str(e)}


# Singleton instances
workflow_executor = WorkflowToolExecutor()
hook_executor = HookToolExecutor()
scheduled_task_executor = ScheduledTaskToolExecutor()
notification_executor = NotificationToolExecutor()

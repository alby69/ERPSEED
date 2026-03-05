"""
AI Assistant Service for FlaskERP
Uses LLM to generate ERP configurations from natural language
With RAG Context Injection and Tool Calling support
"""

import json
import os
import logging
from typing import Optional, Dict, Any, List

from backend.ai.context import get_project_context, get_conversation_context
from backend.ai.tool_registry import tool_registry
from backend.ai.adapters import get_adapter, LLMAdapter
from backend.models import AIConversation, db

logger = logging.getLogger(__name__)


class AIService:
    """Service for interacting with AI models with RAG and Tool Calling"""

    def __init__(self, model: str = None, provider: str = None):
        self.provider_name = provider or os.environ.get("LLM_PROVIDER", "openrouter")
        self.adapter: LLMAdapter = get_adapter(self.provider_name)

        self.model = model or self._get_default_model()
        self.tools = self._get_tool_definitions()
        self._register_tool_handlers()

    def _get_default_model(self) -> str:
        """Ottiene il modello default in base al provider."""
        if self.provider_name == "anthropic":
            return "claude-sonnet-4-20250514"
        return "deepseek/deepseek-chat-v3-0324"

    def _register_tool_handlers(self):
        """Registra gli handler per i tool."""
        tool_registry.register_handler("generate_json", self._handle_generate_json)
        tool_registry.register_handler("apply_config", self._handle_apply_config)
        tool_registry.register_handler("create_workflow", self._handle_create_workflow)

        from backend.ai.tool_executors import (
            workflow_executor,
            hook_executor,
            scheduled_task_executor,
            notification_executor,
            ui_executor,
        )

        # UI Builder tools
        tool_registry.register_handler("create_ui_view", ui_executor.create_ui_view)
        tool_registry.register_handler("add_ui_component", ui_executor.add_ui_component)
        tool_registry.register_handler(
            "update_ui_view_config", ui_executor.update_ui_view_config
        )

        tool_registry.register_handler(
            "create_workflow_automation", self._handle_create_workflow_automation
        )
        tool_registry.register_handler("update_workflow", self._handle_update_workflow)
        tool_registry.register_handler("delete_workflow", self._handle_delete_workflow)
        tool_registry.register_handler(
            "register_business_rule", self._handle_register_business_rule
        )
        tool_registry.register_handler(
            "list_business_rules", self._handle_list_business_rules
        )
        tool_registry.register_handler(
            "delete_business_rule", self._handle_delete_business_rule
        )
        tool_registry.register_handler(
            "create_scheduled_task", self._handle_create_scheduled_task
        )
        tool_registry.register_handler(
            "delete_scheduled_task", self._handle_delete_scheduled_task
        )
        tool_registry.register_handler(
            "setup_notification", self._handle_setup_notification
        )

        tool_registry.register_handler(
            "generate_test_suite", self._handle_generate_test_suite
        )
        tool_registry.register_handler(
            "list_test_suites", self._handle_list_test_suites
        )
        tool_registry.register_handler("run_test_suite", self._handle_run_test_suite)

    def _get_tool_definitions(self) -> List[Dict]:
        """Define available tools for the AI to use"""
        base_tools = [
            {
                "name": "generate_json",
                "description": "Generate FlaskERP configuration as JSON without applying it. Use this when user wants to review or edit the config before applying.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_request": {
                            "type": "string",
                            "description": "The user's natural language request",
                        }
                    },
                    "required": ["user_request"],
                },
            },
            {
                "name": "apply_config",
                "description": "Apply a generated configuration to create actual models, fields, and tables in FlaskERP. Use after generating JSON to create the entities.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "config": {
                            "type": "object",
                            "description": "The JSON configuration to apply",
                        }
                    },
                    "required": ["config"],
                },
            },
            {
                "name": "create_workflow",
                "description": "Create a workflow automation in FlaskERP",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "workflow_config": {
                            "type": "object",
                            "description": "Workflow configuration including name, trigger, and steps",
                        }
                    },
                    "required": ["workflow_config"],
                },
            },
        ]
        return base_tools

    def get_tools_for_project(self, project_id: int) -> List[Dict]:
        """Ottiene i tool dinamici per un progetto."""
        return tool_registry.get_tools_for_project(
            project_id, provider=self.provider_name
        )

    def get_all_tools(self, project_id: int = None) -> List[Dict]:
        """Ottiene tutti i tool disponibili (base + dinamici + business logic + test)."""
        tools = self.tools.copy()

        if project_id:
            try:
                dynamic_tools = self.get_tools_for_project(project_id)
                tools.extend(dynamic_tools)

                business_logic_tools = tool_registry.get_business_logic_tools(
                    project_id
                )
                tools.extend(business_logic_tools)

                test_tools = tool_registry.get_test_tools(project_id)
                tools.extend(test_tools)

                ui_tools = tool_registry.get_ui_builder_tools(project_id)
                tools.extend(ui_tools)
            except Exception as e:
                logger.warning(f"Error getting dynamic tools: {e}")
        else:
            try:
                test_tools = tool_registry.get_test_tools()
                tools.extend(test_tools)
            except Exception as e:
                logger.warning(f"Error getting test tools: {e}")

        return self.adapter.format_tools(tools)

    def generate_erp_config(
        self,
        user_request: str,
        project_id: int,
        user_id: Optional[int] = None,
        apply_directly: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate ERP configuration from natural language request

        Args:
            user_request: Natural language description of what the user wants
            project_id: Target project ID
            user_id: ID of the user making the request
            apply_directly: If True, apply the config immediately

        Returns:
            Dictionary containing generated configuration and metadata
        """
        logger.info(f"AI: Generating config for request: {user_request[:50]}...")

        system_prompt = self._build_system_prompt(project_id)
        user_prompt = self._build_user_prompt(user_request, project_id)

        response = self._call_llm_with_tools(system_prompt, user_prompt, project_id=project_id)

        # Parse response and handle tools
        result = self._handle_response(
            response, user_request, project_id, user_id, apply_directly
        )

        # Convert simple config to a structured execution plan
        if result.get("success") and "config" in result:
            result["plan"] = self._generate_execution_plan(result["config"])

        return result

    def _generate_execution_plan(self, config: Dict) -> List[Dict]:
        """Converts a configuration into a structured execution plan."""
        plan = []

        # Models
        for model in config.get("models", []):
            plan.append({
                "action": "create_model",
                "target": model.get("name"),
                "description": f"Crea nuovo modello '{model.get('name')}'",
                "details": {
                    "table": model.get("table"),
                    "fields_count": len(model.get("fields", []))
                }
            })
            for field in model.get("fields", []):
                plan.append({
                    "action": "add_field",
                    "target": f"{model.get('name')}.{field.get('name')}",
                    "description": f"Aggiungi campo '{field.get('label')}' ({field.get('type')})",
                    "details": field
                })

        # Views
        for view in config.get("views", []):
            plan.append({
                "action": "create_view",
                "target": view.get("name"),
                "description": f"Crea vista {view.get('type')} per {view.get('model')}",
                "details": view
            })

        # Workflows
        for wf in config.get("workflows", []):
            plan.append({
                "action": "create_workflow",
                "target": wf.get("name"),
                "description": f"Crea automazione: {wf.get('name')}",
                "details": wf
            })

        return plan

    def _build_system_prompt(self, project_id: int) -> str:
        """Build system prompt with project context (RAG)"""

        # Get project context via RAG
        project_context = get_project_context(project_id)
        conversation_context = get_conversation_context(project_id, limit=3)

        return f"""You are FlaskERP AI Assistant, an expert in configuring FlaskERP - a no-code ERP platform.

## YOUR ROLE
You help users create and manage ERP components (models, fields, workflows, modules) through natural language.
You generate structured configurations that will be presented as an execution plan to the user.

## PROJECT CONTEXT
{project_context}

{conversation_context}

## AVAILABLE FIELD TYPES
- string: Short text (max 255 chars)
- text: Long text
- integer: Whole numbers
- decimal: Numbers with decimals
- boolean: True/False
- date: Calendar date
- datetime: Date and time
- select: Dropdown with options
- relation: Foreign key to another model (use 'target_table' in options)
- calculated: Computed field with formula
- summary: Aggregate from related records
- file: File upload
- image: Image upload
- json: JSON data

## RELATION CONFIGURATION
For relations (1:N), use type: "relation" and set options:
{{"target_table": "model_name", "field_label": "Display Name"}}

## VALIDATION OPTIONS
- required: Boolean
- is_unique: Boolean
- regex_pattern: String (validation regex)
- min_value, max_value: For numbers
- min_length, max_length: For strings

## IMPORTANT RULES
1. Always use the existing models in the project when creating relations
2. Don't duplicate existing fields - check the project context first
3. Generate clean, valid JSON
4. Use tool calls appropriately:
   - Use 'generate_json' to create config for review
   - Use 'apply_config' to create actual database entities

## RESPONSE FORMAT
When NOT using tools, respond with valid JSON in this format:
{{
  "models": [{{
    "name": "ModelName",
    "table": "table_name", 
    "description": "...",
    "fields": [{{
      "name": "field_name",
      "type": "string",
      "label": "Field Label",
      "required": false,
      "options": {{}}  // For select, relation, etc.
    }}]
  }}]
}}

Start by understanding the user's request, then use the appropriate tool or generate JSON."""

    def _build_user_prompt(self, user_request: str, project_id: int) -> str:
        """Build user prompt"""
        return f"""Project ID: {project_id}

User Request: {user_request}

What would you like me to create or modify? I'll analyze the project context and help you build the best solution."""

    def _call_llm_with_tools(
        self, system_prompt: str, user_prompt: str, project_id: int = None
    ) -> Dict[str, Any]:
        """Call LLM API with tool calling support using adapter"""
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            tools = self.get_all_tools(project_id)

            llm_response = self.adapter.chat(
                messages=messages,
                tools=tools,
                model=self.model,
                temperature=0.3,
                max_tokens=2000,
            )

            logger.info(f"AI response: {llm_response.raw}")

            if llm_response.has_tool_calls:
                return self._handle_tool_calls(llm_response, project_id)

            return {
                "content": llm_response.content,
                "raw": llm_response.raw,
            }

        except Exception as e:
            logger.error(f"AI call error: {e}")
            return {"error": str(e)}

    def _handle_tool_calls(self, llm_response, project_id: int) -> Dict[str, Any]:
        """Gestisce le chiamate tool dalla risposta LLM."""
        results = []

        for tool_call in llm_response.tool_calls:
            tool_name = tool_call.name
            tool_args = tool_call.arguments

            logger.info(f"AI used tool: {tool_name}")

            try:
                result = tool_registry.execute_tool(
                    tool_name, tool_args, {"project_id": project_id}
                )
                results.append(
                    {"tool": tool_name, "result": result, "tool_id": tool_call.tool_id}
                )
            except ValueError as e:
                logger.warning(f"Tool not found: {tool_name}")
                results.append(
                    {"tool": tool_name, "error": str(e), "tool_id": tool_call.tool_id}
                )
            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {e}")
                results.append(
                    {"tool": tool_name, "error": str(e), "tool_id": tool_call.tool_id}
                )

        return {
            "tool_calls": results,
            "has_more": llm_response.stop_reason == "tool_use",
            "raw": llm_response.raw,
        }

    def _handle_response(
        self,
        response: Dict,
        user_request: str,
        project_id: int,
        user_id: Optional[int],
        apply_directly: bool,
    ) -> Dict[str, Any]:
        """Handle the AI response, including tool calls"""

        try:
            if "error" in response:
                return {"success": False, "error": response["error"]}

            # Check for tool calls in response
            if "choices" in response and len(response["choices"]) > 0:
                message = response["choices"][0].get("message", {})

                # Check if AI used a tool
                if "tool_calls" in message:
                    tool_calls = message["tool_calls"]
                    results = []

                    for tool_call in tool_calls:
                        tool_name = tool_call["function"]["name"]
                        tool_args = json.loads(tool_call["function"]["arguments"])

                        logger.info(f"AI used tool: {tool_name}")

                        if tool_name == "generate_json":
                            # Generate JSON config
                            result = self._generate_config_internal(
                                tool_args.get("user_request", user_request), project_id
                            )
                            results.append({"tool": "generate_json", "result": result})

                        elif tool_name == "apply_config":
                            # Apply config directly
                            result = self._apply_config_internal(
                                tool_args.get("config", {}), project_id, user_id
                            )
                            results.append({"tool": "apply_config", "result": result})

                    if results:
                        return {
                            "success": True,
                            "tool_calls": results,
                            "message": f"Executed {len(results)} tool(s)",
                        }

                # No tool call - parse JSON from content
                content = message.get("content", "")
                return self._parse_response(content, user_request)

            return {"success": False, "error": "No response from AI"}

        except Exception as e:
            logger.error(f"Error handling response: {e}")
            return {"success": False, "error": str(e)}

    def _generate_config_internal(self, user_request: str, project_id: int) -> Dict:
        """Internal method to generate config"""
        # Simple generation without tools
        system_prompt = self._build_system_prompt(project_id)
        user_prompt = f"Generate FlaskERP configuration: {user_request}"

        response = self._call_llm_simple(system_prompt, user_prompt)
        return self._parse_response(response, user_request)

    def _apply_config_internal(
        self, config: Dict, project_id: int, user_id: Optional[int]
    ) -> Dict[str, Any]:
        """Apply configuration to create actual entities - returns config for UI"""
        try:
            # For now, return the config so user can review and apply via UI
            # This is safer and gives user control
            return {
                "success": True,
                "config": config,
                "message": "Configurazione generata. Puoi applicarla tramite il Builder.",
                "action_required": "review_and_apply",
            }

        except Exception as e:
            logger.error(f"Error preparing config: {e}")
            return {"success": False, "error": str(e)}

    def _call_llm_simple(self, system_prompt: str, user_prompt: str) -> str:
        """Simple LLM call without tools using adapter"""
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            llm_response = self.adapter.chat(
                messages=messages,
                model=self.model,
                temperature=0.3,
                max_tokens=1500,
            )

            if llm_response.content:
                return llm_response.content

            return json.dumps({"error": "No response"})

        except Exception as e:
            return json.dumps({"error": str(e)})

    def _handle_generate_json(self, args: Dict, context: Dict) -> Dict:
        """Handler per il tool generate_json."""
        user_request = args.get("user_request", "")
        project_id = context.get("project_id")
        return self._generate_config_internal(user_request, project_id)

    def _handle_apply_config(self, args: Dict, context: Dict) -> Dict:
        """Handler per il tool apply_config."""
        config = args.get("config", {})
        project_id = context.get("project_id")
        user_id = context.get("user_id")
        return self._apply_config_internal(config, project_id, user_id)

    def _handle_create_workflow(self, args: Dict, context: Dict) -> Dict:
        """Handler per il tool create_workflow."""
        workflow_config = args.get("workflow_config", {})
        return {
            "success": True,
            "message": "Workflow creation not yet implemented",
            "config": workflow_config,
        }

    def _parse_response(self, response: str, user_request: str) -> Dict[str, Any]:
        """Parse the LLM response into a structured format"""

        # Check for error in response
        try:
            error_check = json.loads(response)
            if "error" in error_check:
                return {
                    "success": False,
                    "error": error_check["error"],
                    "user_request": user_request,
                }
        except:
            pass

        try:
            import re

            # Clean up the response
            json_str = response.strip()

            # Remove markdown code blocks
            json_str = re.sub(r"^```json\s*", "", json_str)
            json_str = re.sub(r"^```\s*", "", json_str)
            json_str = re.sub(r"\s*```$", "", json_str)

            # Find JSON block
            brace_start = json_str.find("{")
            if brace_start > 0:
                json_str = json_str[brace_start:]

            # Find closing brace
            brace_end = json_str.rfind("}")
            if brace_end >= 0:
                json_str = json_str[: brace_end + 1]

            # Fix common JSON issues
            json_str = re.sub(r",(\s*[}\]])", r"\1", json_str)
            json_str = re.sub(r"\btrue\b", "true", json_str)
            json_str = re.sub(r"\bfalse\b", "false", json_str)
            json_str = re.sub(r"\bnull\b", "null", json_str)

            # Remove extra fields that AI sometimes adds
            json_str = re.sub(r',?\s*"relations"\s*:\s*\[[^\]]*\]', "", json_str)
            json_str = re.sub(r',?\s*"foreign_keys"\s*:\s*\[[^\]]*\]', "", json_str)

            config = json.loads(json_str)

            return {
                "success": True,
                "config": config,
                "user_request": user_request,
                "message": "Configurazione generata con successo",
            }

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            logger.error(f"Raw response: {response[:500]}")
            return {
                "success": False,
                "error": f"Parse error: {str(e)}",
                "raw_response": response[:500],
                "user_request": user_request,
            }

    def save_conversation(
        self,
        project_id: int,
        user_id: int,
        user_message: str,
        ai_response: str,
        was_successful: bool = False,
        user_correction: Optional[str] = None,
        action_taken: Optional[str] = None,
    ) -> bool:
        """Save conversation to database for learning"""
        try:
            conversation = AIConversation(
                project_id=project_id,
                user_id=user_id,
                user_message=user_message,
                ai_response=ai_response[:5000] if ai_response else None,
                was_successful=was_successful,
                user_correction=user_correction,
                action_taken=action_taken,
                context_snapshot=get_project_context(project_id),
            )
            db.session.add(conversation)
            db.session.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            return False

    def _handle_create_workflow_automation(self, args: Dict, context: Dict) -> Dict:
        """Handler per il tool create_workflow_automation."""
        from backend.ai.tool_executors import workflow_executor

        return workflow_executor.create_workflow_automation(args, context)

    def _handle_update_workflow(self, args: Dict, context: Dict) -> Dict:
        """Handler per il tool update_workflow."""
        from backend.ai.tool_executors import workflow_executor

        return workflow_executor.update_workflow(args, context)

    def _handle_delete_workflow(self, args: Dict, context: Dict) -> Dict:
        """Handler per il tool delete_workflow."""
        from backend.ai.tool_executors import workflow_executor

        return workflow_executor.delete_workflow(args, context)

    def _handle_register_business_rule(self, args: Dict, context: Dict) -> Dict:
        """Handler per il tool register_business_rule."""
        from backend.ai.tool_executors import hook_executor

        return hook_executor.register_business_rule(args, context)

    def _handle_list_business_rules(self, args: Dict, context: Dict) -> Dict:
        """Handler per il tool list_business_rules."""
        from backend.ai.tool_executors import hook_executor

        return hook_executor.list_business_rules(args, context)

    def _handle_delete_business_rule(self, args: Dict, context: Dict) -> Dict:
        """Handler per il tool delete_business_rule."""
        from backend.ai.tool_executors import hook_executor

        return hook_executor.delete_business_rule(args, context)

    def _handle_create_scheduled_task(self, args: Dict, context: Dict) -> Dict:
        """Handler per il tool create_scheduled_task."""
        from backend.ai.tool_executors import scheduled_task_executor

        return scheduled_task_executor.create_scheduled_task(args, context)

    def _handle_delete_scheduled_task(self, args: Dict, context: Dict) -> Dict:
        """Handler per il tool delete_scheduled_task."""
        from backend.ai.tool_executors import scheduled_task_executor

        return scheduled_task_executor.delete_scheduled_task(args, context)

    def _handle_setup_notification(self, args: Dict, context: Dict) -> Dict:
        """Handler per il tool setup_notification."""
        from backend.ai.tool_executors import notification_executor

        return notification_executor.setup_notification(args, context)

    def _handle_generate_test_suite(self, args: Dict, context: Dict) -> Dict:
        """Handler per il tool generate_test_suite."""
        from backend.ai.test_generator import ai_test_generator
        from backend.models import SysModel

        model_name = args.get("model_name")
        project_id = context.get("project_id", args.get("project_id"))
        test_types = args.get(
            "test_types", ["create", "read", "update", "delete", "validation"]
        )
        save_to_db = args.get("save_to_db", True)

        if not model_name:
            return {"success": False, "error": "model_name is required"}

        if not project_id:
            return {"success": False, "error": "project_id is required"}

        sys_model = SysModel.query.filter_by(
            project_id=project_id, name=model_name, status="published"
        ).first()

        if not sys_model:
            return {
                "success": False,
                "error": f"Model '{model_name}' not found or not published",
            }

        result = ai_test_generator.generate_test_suite(
            sys_model, project_id, test_types
        )

        if save_to_db:
            save_result = ai_test_generator.save_test_suite(
                result["test_suite"], result["test_cases"], project_id
            )
            return {
                "success": True,
                "test_suite": result["test_suite"],
                "test_cases": result["test_cases"],
                "summary": result["summary"],
                "saved": save_result,
            }

        return {
            "success": True,
            "test_suite": result["test_suite"],
            "test_cases": result["test_cases"],
            "summary": result["summary"],
            "saved": False,
        }

    def _handle_list_test_suites(self, args: Dict, context: Dict) -> Dict:
        """Handler per il tool list_test_suites."""
        from backend.core.models.test_models import TestSuite
        from backend.models import SysModel

        project_id = context.get("project_id", args.get("project_id"))

        if not project_id:
            return {"success": False, "error": "project_id is required"}

        model_names = [
            m.name
            for m in SysModel.query.filter_by(
                project_id=project_id, status="published"
            ).all()
        ]

        suites = (
            TestSuite.query.filter(TestSuite.modulo_target.in_(model_names)).all()
            if model_names
            else []
        )

        return {
            "success": True,
            "test_suites": [
                {
                    "id": s.id,
                    "nome": s.nome,
                    "descrizione": s.descrizione,
                    "modulo_target": s.modulo_target,
                    "test_type": s.test_type,
                    "stato": s.stato,
                    "is_active": s.is_active,
                }
                for s in suites
            ],
        }

    def _handle_run_test_suite(self, args: Dict, context: Dict) -> Dict:
        """Handler per il tool run_test_suite."""
        suite_id = args.get("suite_id")

        if not suite_id:
            return {"success": False, "error": "suite_id is required"}

        return {
            "success": True,
            "message": f"Test suite {suite_id} execution started",
            "note": "Use Test Runner UI to view results",
        }


# Legacy compatibility - keep old method name
def get_ai_service():
    """Get the AI service singleton"""
    return AIService()


ai_service = AIService()

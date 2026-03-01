"""
AI Assistant Service for FlaskERP
Uses LLM to generate ERP configurations from natural language
With RAG Context Injection and Tool Calling support
"""

import json
import os
import requests
import logging
from typing import Optional, Dict, Any, List, Callable

from backend.ai.context import get_project_context, get_conversation_context
from backend.models import AIConversation, db

logger = logging.getLogger(__name__)


class AIService:
    """Service for interacting with AI models via OpenRouter with RAG and Tool Calling"""

    def __init__(self, model: str = "deepseek/deepseek-chat-v3-0324"):
        self.model = model
        self.api_key = os.environ.get(
            "OPENROUTER_API_KEY",
            "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",
        )
        self.base_url = "https://openrouter.ai/api/v1"
        self.tools = self._get_tool_definitions()

    def _get_tool_definitions(self) -> List[Dict]:
        """Define available tools for the AI to use"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "generate_json",
                    "description": "Generate FlaskERP configuration as JSON without applying it. Use this when user wants to review or edit the config before applying.",
                    "parameters": {
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
            },
            {
                "type": "function",
                "function": {
                    "name": "apply_config",
                    "description": "Apply a generated configuration to create actual models, fields, and tables in FlaskERP. Use after generating JSON to create the entities.",
                    "parameters": {
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
            },
            {
                "type": "function",
                "function": {
                    "name": "create_workflow",
                    "description": "Create a workflow automation in FlaskERP",
                    "parameters": {
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
            },
        ]

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

        response = self._call_llm_with_tools(system_prompt, user_prompt)

        # Parse response and handle tools
        result = self._handle_response(
            response, user_request, project_id, user_id, apply_directly
        )

        return result

    def _build_system_prompt(self, project_id: int) -> str:
        """Build system prompt with project context (RAG)"""

        # Get project context via RAG
        project_context = get_project_context(project_id)
        conversation_context = get_conversation_context(project_id, limit=3)

        return f"""You are FlaskERP AI Assistant, an expert in configuring FlaskERP - a no-code ERP platform.

## YOUR ROLE
You help users create and manage ERP components (models, fields, workflows, modules) through natural language.

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
        self, system_prompt: str, user_prompt: str
    ) -> Dict[str, Any]:
        """Call OpenRouter API with tool calling support"""
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://flaskerp.local",
                    "X-Title": "FlaskERP AI Assistant",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "tools": self.tools,
                    "tool_choice": "auto",
                    "temperature": 0.3,
                    "max_tokens": 2000,
                },
                timeout=60,
            )

            logger.info(f"AI API response status: {response.status_code}")

            if response.status_code != 200:
                logger.error(f"AI API error: {response.text}")
                return {
                    "error": f"API Error: {response.status_code}",
                    "text": response.text,
                }

            result = response.json()
            logger.info(f"AI response: {json.dumps(result)[:500]}")

            return result

        except Exception as e:
            logger.error(f"AI call error: {e}")
            return {"error": str(e)}

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
        """Simple LLM call without tools"""
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://flaskerp.local",
                    "X-Title": "FlaskERP AI Assistant",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1500,
                },
                timeout=30,
            )

            if response.status_code != 200:
                return json.dumps({"error": f"API Error: {response.status_code}"})

            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]

            return json.dumps({"error": "No response"})

        except Exception as e:
            return json.dumps({"error": str(e)})

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


# Legacy compatibility - keep old method name
def get_ai_service():
    """Get the AI service singleton"""
    return AIService()


ai_service = AIService()

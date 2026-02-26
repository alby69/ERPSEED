"""
AI Assistant Service for FlaskERP
Uses LLM to generate ERP configurations from natural language
"""

import json
import os
import requests
from typing import Optional, Dict, Any, List


class AIService:
    """Service for interacting with AI models via OpenRouter"""

    def __init__(self, model: str = "nvidia/nemotron-nano-9b-v2:free"):
        self.model = model
        self.api_key = os.environ.get(
            "OPENROUTER_API_KEY",
            "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",
        )
        self.base_url = "https://openrouter.ai/api/v1"

    def generate_erp_config(self, user_request: str, project_id: int) -> Dict[str, Any]:
        """
        Generate ERP configuration from natural language request

        Args:
            user_request: Natural language description of what the user wants
            project_id: Target project ID

        Returns:
            Dictionary containing generated configuration and metadata
        """
        import logging

        logging.info(f"AI: Generating config for request: {user_request[:50]}...")

        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(user_request, project_id)

        response = self._call_llm(system_prompt, user_prompt)

        logging.info(f"AI: Raw response length: {len(response)}")

        return self._parse_response(response, user_request)

    def _build_system_prompt(self) -> str:
        """Build the system prompt that defines AI behavior"""
        return """You are an ERP configuration assistant for FlaskERP. Generate valid JSON only.

Field types: string, text, integer, decimal, boolean, date, datetime, select, relation, calculated, summary, lookup.

Example:
User: "Create a module for suppliers with name, email"
Response: {"models": [{"name": "Fornitore", "table": "fornitori", "description": "Elenco fornitori", "fields": [{"name": "nome", "type": "string", "label": "Nome", "required": true}, {"name": "email", "type": "string", "label": "Email"}]}]}

Always respond with JSON only, no additional text."""

    def _build_user_prompt(self, user_request: str, project_id: int) -> str:
        """Build the user prompt with the specific request"""
        return f"""Project ID: {project_id}

User Request: {user_request}

Generate the FlaskERP configuration in JSON format:"""

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call the OpenRouter API (synchronous)
        """
        import logging

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
                    "temperature": 0.7,
                    "max_tokens": 2000,
                },
                timeout=60,
            )

            logging.info(f"AI API response status: {response.status_code}")
            logging.info(f"AI API response text: {response.text[:1000]}")

            if response.status_code != 200:
                return json.dumps(
                    {"error": f"API Error {response.status_code}: {response.text}"}
                )

            result = response.json()

            logging.info(f"AI full response: {result}")

            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                logging.info(f"AI content: {content[:500]}")
                return content
            elif "error" in result:
                return json.dumps({"error": result["error"]})
            else:
                return json.dumps({"error": "Unexpected response format"})

        except requests.exceptions.RequestException as e:
            logging.error(f"AI connection error: {e}")
            return json.dumps({"error": f"Connection error: {str(e)}"})
        except Exception as e:
            logging.error(f"AI error: {e}")
            return json.dumps({"error": f"Error: {str(e)}"})

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
            # Try to extract JSON from response
            json_str = response.strip()

            # Fix common JSON issues from LLM
            import re

            # Remove trailing commas before closing braces/brackets (multiple passes)
            for _ in range(3):
                json_str = re.sub(r",(\s*[}\]])", r"\1", json_str)

            # Also fix unquoted booleans/null
            json_str = re.sub(r"\btrue\b", "true", json_str)
            json_str = re.sub(r"\bfalse\b", "false", json_str)
            json_str = re.sub(r"\bnull\b", "null", json_str)

            # If response starts with text before JSON, try to extract JSON
            if not json_str.startswith("{") and not json_str.startswith("["):
                # Try to find JSON in the response
                match = re.search(r"[\[{]", json_str)
                if match:
                    json_str = json_str[match.start() :]
                    # Also try to find where JSON ends
                    end_match = re.search(r"}[\] ]*$", json_str)
                    if end_match:
                        json_str = json_str[: end_match.end()]

            if json_str.startswith("```"):
                parts = json_str.split("```")
                for part in parts:
                    if part.strip() and not part.strip().startswith("json"):
                        try:
                            config = json.loads(part.strip())
                            return {
                                "success": True,
                                "config": config,
                                "user_request": user_request,
                                "message": "Configurazione generata con successo",
                            }
                        except:
                            continue

            config = json.loads(json_str)

            return {
                "success": True,
                "config": config,
                "user_request": user_request,
                "message": "Configurazione generata con successo",
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Errore nel parsing della risposta: {str(e)}",
                "raw_response": response[:500],
                "user_request": user_request,
            }

    def chat(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        General chat with the AI assistant
        Can answer questions about FlaskERP or help with configurations
        """
        system_prompt = """You are a helpful ERP assistant for FlaskERP. 

You can help users with:
- Understanding FlaskERP concepts and architecture
- Designing data models for their business
- Configuring the system
- Troubleshooting issues

Be concise, friendly, and practical. Use Italian if the user writes in Italian."""

        if context:
            system_prompt += f"\n\nCurrent context: {json.dumps(context)}"

        response = self._call_llm(system_prompt, message)

        return {"success": True, "message": response, "user_message": message}

    def suggest_improvements(self, model_config: Dict[str, Any]) -> List[str]:
        """
        Analyze an existing model configuration and suggest improvements
        """
        system_prompt = """You are an ERP design expert. Analyze the following model configuration 
and suggest improvements. Consider:
- Missing fields that would be useful
- Better field types
- Additional relationships
- Validations that should be added
- Performance considerations

Respond with a JSON array of suggestions."""

        response = self._call_llm(system_prompt, json.dumps(model_config, indent=2))

        try:
            suggestions = json.loads(response)
            return suggestions if isinstance(suggestions, list) else []
        except:
            return ["Analisi non disponibile"]


# Singleton instance
ai_service = AIService()


def get_ai_service() -> AIService:
    """Get the AI service singleton"""
    return ai_service

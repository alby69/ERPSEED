"""
Chat Service - Domain service for AI chat interactions.
"""

import logging
from typing import List, Dict, Any, Optional

from ..ports.llm_port import ChatCompletion, ToolCall

logger = logging.getLogger(__name__)


class ChatService:
    """Service for managing AI chat interactions."""

    def __init__(
        self,
        llm_port,
        tool_service=None,
        system_prompt: str = None,
    ):
        self.llm_port = llm_port
        self.tool_service = tool_service
        self.system_prompt = system_prompt or self._default_system_prompt()

    def _default_system_prompt(self) -> str:
        return """You are FlaskERP AI Assistant, an expert in configuring FlaskERP - a no-code ERP platform.

You help users create and manage ERP components (models, fields, workflows, modules) through natural language.
Always respond in Italian unless the user asks otherwise."""

    def chat(
        self,
        user_message: str,
        history: List[Dict] = None,
        tools: List[Dict] = None,
        context: Dict = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Process a chat message and return response.

        Args:
            user_message: The user's message
            history: Previous messages in conversation
            tools: Available tools for the AI
            context: Additional context (project info, etc.)

        Returns:
            Dict with response content and metadata
        """
        messages = self._build_messages(user_message, history, context)

        if tools is None and self.tool_service:
            tools = self.tool_service.get_tool_definitions()

        try:
            response = self.llm_port.chat(messages=messages, tools=tools, **kwargs)

            result = {
                "content": response.content,
                "model": response.model,
                "finish_reason": response.finish_reason,
            }

            if response.has_tool_calls:
                tool_results = self._handle_tool_calls(response.tool_calls, context)
                result["tool_calls"] = response.tool_calls
                result["tool_results"] = tool_results

            return result

        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {"error": str(e), "content": None}

    def _build_messages(
        self,
        user_message: str,
        history: List[Dict] = None,
        context: Dict = None,
    ) -> List[Dict]:
        """Build message list for LLM."""
        messages = []

        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})

        if context:
            context_str = self._format_context(context)
            if context_str:
                messages.append(
                    {"role": "system", "content": f"Context:\n{context_str}"}
                )

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": user_message})

        return messages

    def _format_context(self, context: Dict) -> str:
        """Format context information."""
        parts = []

        if context.get("project_name"):
            parts.append(f"Project: {context['project_name']}")

        if context.get("models"):
            names = [m.get("name", m.get("table")) for m in context["models"][:10]]
            parts.append(f"Models: {', '.join(names)}")

        if context.get("workflows"):
            names = [w.get("name") for w in context["workflows"][:5]]
            parts.append(f"Workflows: {', '.join(names)}")

        return "\n".join(parts)

    def _handle_tool_calls(
        self,
        tool_calls: List[ToolCall],
        context: Dict,
    ) -> List[Dict]:
        """Process tool calls from LLM."""
        results = []

        for tool_call in tool_calls:
            try:
                if self.tool_service:
                    result = self.tool_service.execute(
                        tool_call.name, tool_call.arguments, context or {}
                    )
                else:
                    result = {"error": "Tool service not configured"}

                results.append(
                    {
                        "tool": tool_call.name,
                        "tool_id": tool_call.tool_id,
                        "result": result,
                    }
                )
            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                results.append(
                    {
                        "tool": tool_call.name,
                        "tool_id": tool_call.tool_id,
                        "error": str(e),
                    }
                )

        return results

    def stream_chat(
        self,
        user_message: str,
        history: List[Dict] = None,
        tools: List[Dict] = None,
        context: Dict = None,
        **kwargs,
    ):
        """Stream chat response."""
        if not hasattr(self.llm_port, "stream_chat"):
            raise NotImplementedError(
                f"{self.llm_port.name} does not support streaming"
            )

        messages = self._build_messages(user_message, history, context)

        for chunk in self.llm_port.stream_chat(
            messages=messages, tools=tools, **kwargs
        ):
            yield chunk

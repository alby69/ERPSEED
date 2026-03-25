"""
AI Services - Chat and Tool services.
"""
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


DEFAULT_SYSTEM_PROMPT = """You are ERPSeed AI Assistant, an expert in configuring ERPSeed - a no-code ERP platform.

You help users create and manage ERP components (models, fields, workflows, modules) through natural language.
Always respond in Italian unless the user asks otherwise."""


class ChatService:
    def __init__(self, llm_adapter, tool_service=None, system_prompt: str = None):
        self.llm_adapter = llm_adapter
        self.tool_service = tool_service
        self.system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT

    def chat(self, user_message: str, history: List[Dict] = None, tools: List[Dict] = None,
             context: Dict = None, **kwargs) -> Dict[str, Any]:
        messages = self._build_messages(user_message, history, context)
        try:
            response = self.llm_adapter.chat(messages=messages, tools=tools, **kwargs)
            result = {"content": response.content, "model": response.model, "finish_reason": response.finish_reason}
            if response.has_tool_calls:
                result["tool_calls"] = response.tool_calls
                result["tool_results"] = self._handle_tool_calls(response.tool_calls, context or {})
            return result
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {"error": str(e), "content": None}

    def _build_messages(self, user_message: str, history: List[Dict], context: Dict) -> List[Dict]:
        messages = [{"role": "system", "content": self.system_prompt}]
        if context:
            context_str = self._format_context(context)
            if context_str: messages.append({"role": "system", "content": f"Context:\n{context_str}"})
        if history: messages.extend(history)
        messages.append({"role": "user", "content": user_message})
        return messages

    def _format_context(self, context: Dict) -> str:
        parts = []
        if context.get("project_name"): parts.append(f"Project: {context['project_name']}")
        if context.get("models"):
            names = [m.get("name", m.get("table")) for m in context["models"][:10]]
            parts.append(f"Models: {', '.join(names)}")
        return "\n".join(parts)

    def _handle_tool_calls(self, tool_calls: List[Dict], context: Dict) -> List[Dict]:
        results = []
        for tc in tool_calls:
            try:
                result = self.tool_service.execute(tc.get("name"), tc.get("arguments", {}), context) if self.tool_service else {}
                results.append({"tool": tc.get("name"), "tool_id": tc.get("id"), "result": result})
            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                results.append({"tool": tc.get("name"), "tool_id": tc.get("id"), "error": str(e)})
        return results


class ToolService:
    def __init__(self, tools: List[Dict] = None):
        self._tools: Dict[str, Dict] = {}
        if tools:
            for t in tools: self.register(t)

    def register(self, tool: Dict[str, Any]) -> None:
        self._tools[tool["name"]] = tool

    def get_tool_definitions(self) -> List[Dict]:
        return [t for t in self._tools.values() if t.get("is_enabled", True)]

    def execute(self, tool_name: str, arguments: Dict, context: Dict) -> Any:
        tool = self._tools.get(tool_name)
        if not tool:
            return {"error": f"Tool not found: {tool_name}"}
        handler = tool.get("handler")
        if not handler:
            return {"error": f"Tool has no handler: {tool_name}"}
        try:
            return handler(arguments, context)
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {"error": str(e)}

"""
Tool Service - Domain service for managing and executing AI tools.
"""

import logging
from typing import Dict, Any, List, Callable, Optional

logger = logging.getLogger(__name__)


class ToolDefinition:
    """Represents a tool available to the AI."""

    def __init__(
        self,
        name: str,
        description: str,
        input_schema: Dict,
        handler: Callable = None,
    ):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.handler = handler

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }


class ToolService:
    """Service for managing AI tools."""

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._handlers: Dict[str, Callable] = {}

    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: Dict,
        handler: Callable = None,
    ) -> None:
        """
        Register a new tool.

        Args:
            name: Tool name
            description: What the tool does
            input_schema: JSON schema for input
            handler: Function to execute the tool
        """
        tool = ToolDefinition(name, description, input_schema, handler)
        self._tools[name] = tool

        if handler:
            self._handlers[name] = handler

        logger.debug(f"Tool registered: {name}")

    def register_handler(self, name: str, handler: Callable) -> None:
        """Register a handler for an existing tool."""
        self._handlers[name] = handler

        if name in self._tools:
            self._tools[name].handler = handler

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """Get a tool by name."""
        return self._tools.get(name)

    def get_tool_definitions(self) -> List[Dict]:
        """Get all tool definitions for LLM."""
        return [tool.to_dict() for tool in self._tools.values()]

    def execute(
        self,
        tool_name: str,
        arguments: Dict,
        context: Dict,
    ) -> Dict[str, Any]:
        """
        Execute a tool.

        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments for the tool
            context: Execution context

        Returns:
            Result from the tool handler
        """
        tool = self._tools.get(tool_name)

        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")

        handler = self._handlers.get(tool_name)

        if not handler:
            raise ValueError(f"No handler for tool: {tool_name}")

        try:
            logger.info(f"Executing tool: {tool_name}")
            result = handler(arguments, context)
            return result
        except Exception as e:
            logger.error(f"Tool execution error: {tool_name} - {e}")
            return {"error": str(e)}

    def has_tool(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name in self._tools

    def unregister_tool(self, name: str) -> bool:
        """Unregister a tool."""
        if name in self._tools:
            del self._tools[name]
            if name in self._handlers:
                del self._handlers[name]
            return True
        return False

    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self._tools.keys())


_default_tool_service: Optional[ToolService] = None


def get_tool_service() -> ToolService:
    """Get the default tool service instance."""
    global _default_tool_service
    if _default_tool_service is None:
        _default_tool_service = ToolService()
    return _default_tool_service

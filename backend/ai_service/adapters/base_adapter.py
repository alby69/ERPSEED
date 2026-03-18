"""
Base adapter for LLM providers.
"""

import json
import logging
from typing import Dict, List, Any

from ..domain.ports.llm_port import LLMPort, ChatCompletion, ToolCall

logger = logging.getLogger(__name__)


class BaseLLMAdapter(LLMAdapter):
    """Base class for LLM adapters with common functionality."""

    def __init__(self, api_key: str = None, default_model: str = None):
        self.api_key = api_key
        self.default_model = default_model

    @property
    def name(self) -> str:
        return self.__class__.__name__.replace("Adapter", "").lower()

    def chat(
        self,
        messages: List[Dict],
        tools: List[Dict] = None,
        model: str = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs,
    ) -> ChatCompletion:
        """Override in subclass."""
        raise NotImplementedError()

    def extract_tool_calls(self, response_data: Dict) -> List[ToolCall]:
        """Override in subclass."""
        return []

    def _parse_tool_calls(
        self, raw_calls: List, arguments_key: str = "function"
    ) -> List[ToolCall]:
        """Helper to parse tool calls from various formats."""
        tool_calls = []

        for tc in raw_calls:
            try:
                func = tc.get(arguments_key, {})
                name = func.get("name")
                arguments_str = func.get("arguments", "{}")

                if isinstance(arguments_str, str):
                    arguments = json.loads(arguments_str)
                else:
                    arguments = arguments_str

                tool_calls.append(
                    ToolCall(name=name, arguments=arguments, tool_id=tc.get("id"))
                )
            except (json.JSONDecodeError, AttributeError) as e:
                logger.warning(f"Error parsing tool call: {e}")
                continue

        return tool_calls

    def _error_response(self, error: str) -> ChatCompletion:
        """Create an error response."""
        return ChatCompletion(
            content=f"Error: {error}",
            raw={"error": error},
        )

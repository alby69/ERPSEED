"""
LLM Port - Interface for LLM providers (Ports & Adapters pattern).

This module defines the abstract interface that all LLM adapters must implement.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncIterator


class Message:
    """Represents a chat message."""

    def __init__(self, role: str, content: str, tool_calls: List = None):
        self.role = role
        self.content = content
        self.tool_calls = tool_calls or []

    def to_dict(self) -> Dict:
        return {
            "role": self.role,
            "content": self.content,
        }


class ToolCall:
    """Represents a tool call from LLM."""

    def __init__(self, name: str, arguments: Dict, tool_id: str = None):
        self.name = name
        self.arguments = arguments
        self.tool_id = tool_id

    def __repr__(self):
        return f"ToolCall(name={self.name}, args={self.arguments})"


class ChatCompletion:
    """Represents a chat completion response."""

    def __init__(
        self,
        content: str = None,
        tool_calls: List[ToolCall] = None,
        finish_reason: str = None,
        model: str = None,
        raw: Dict = None,
    ):
        self.content = content
        self.tool_calls = tool_calls or []
        self.finish_reason = finish_reason
        self.model = model
        self.raw = raw or {}

    @property
    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0


class LLMPort(ABC):
    """
    Abstract port for LLM providers.

    Implement this interface to add support for new LLM providers.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider name."""
        pass

    @abstractmethod
    def chat(
        self,
        messages: List[Dict],
        tools: List[Dict] = None,
        model: str = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs,
    ) -> ChatCompletion:
        """
        Send a chat request to the LLM.

        Args:
            messages: List of message dicts [{"role": "user", "content": "..."}]
            tools: Optional list of tool definitions
            model: Model name (provider-specific)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            **kwargs: Additional provider-specific parameters

        Returns:
            ChatCompletion with response
        """
        pass

    @abstractmethod
    def extract_tool_calls(self, response_data: Dict) -> List[ToolCall]:
        """
        Extract tool calls from provider response.

        Args:
            response_data: Raw response from provider

        Returns:
            List of ToolCall objects
        """
        pass

    def format_tools(self, tools: List[Dict]) -> List[Dict]:
        """
        Format tools for this provider.
        Override for provider-specific formatting.
        """
        return tools

    def list_models(self) -> List[Dict]:
        """
        List available models for this provider.
        Override if supported.
        """
        return []


class StreamingLLMPort(LLMPort):
    """
    Extended port for streaming LLM responses.
    """

    def stream_chat(
        self,
        messages: List[Dict],
        tools: List[Dict] = None,
        model: str = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        on_chunk: callable = None,
        **kwargs,
    ) -> AsyncIterator[str]:
        """
        Stream chat response.

        Args:
            messages: List of messages
            tools: Optional tool definitions
            model: Model name
            temperature: Sampling temperature
            max_tokens: Max tokens
            on_chunk: Callback for each chunk

        Yields:
            Text chunks
        """
        raise NotImplementedError(f"{self.name} does not support streaming")

    def chat(
        self,
        messages: List[Dict],
        tools: List[Dict] = None,
        model: str = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs,
    ) -> ChatCompletion:
        """Default implementation uses non-streaming."""
        raise NotImplementedError("Implement in subclass")

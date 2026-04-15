"""
Base adapter interface for LLM providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class ToolCall:
    """Rappresenta una chiamata a tool estratta dalla risposta LLM."""

    def __init__(self, name: str, arguments: Dict, tool_id: str = None):
        self.name = name
        self.arguments = arguments
        self.tool_id = tool_id

    def __repr__(self):
        return f"ToolCall(name={self.name}, args={self.arguments})"


class LLMResponse:
    """Wrapper per la risposta LLM."""

    def __init__(
        self,
        content: str = None,
        tool_calls: List[ToolCall] = None,
        stop_reason: str = None,
        raw: Dict = None,
    ):
        self.content = content
        self.tool_calls = tool_calls or []
        self.stop_reason = stop_reason
        self.raw = raw or {}

    @property
    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0


class LLMAdapter(ABC):
    """
    Interfaccia base per gli adapter LLM.
    Implementare questa classe per aggiungere nuovi provider.
    """

    @abstractmethod
    def chat(
        self,
        messages: List[Dict],
        tools: List[Dict] = None,
        model: str = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs,
    ) -> LLMResponse:
        """
        Invia un messaggio all'LLM.

        Args:
            messages: Lista di messaggi [{"role": "user", "content": "..."}]
            tools: Lista di definizioni tool
            model: Nome del modello (provider-specific)
            temperature: Temperatura per la generazione
            max_tokens: Token massimi nella risposta

        Returns:
            LLMResponse con contenuto e/o tool_calls
        """
        pass

    @abstractmethod
    def extract_tool_calls(self, response_data: Dict) -> List[ToolCall]:
        """Estrae le chiamate tool dalla risposta del provider."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Nome del provider."""
        pass

    def format_tools(self, tools: List[Dict]) -> List[Dict]:
        """
        Formatta gli strumenti per questo provider.
        Override per provider-specific formatting.
        """
        return tools

    def parse_messages(self, messages: List[Dict]) -> List[Dict]:
        """
        Normalizza i messaggi per il provider.
        """
        return messages


class StreamingLLMAdapter(LLMAdapter):
    """
    Estende LLMAdapter per supportare streaming.
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
    ):
        """
        Versione streaming di chat.

        Args:
            on_chunk: Callback per ogni chunk ricevuto
        """
        raise NotImplementedError("Streaming not implemented for this provider")

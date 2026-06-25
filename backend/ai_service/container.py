"""
AI Service Container - Dependency injection for AI services.
"""

import os
import logging
from typing import Optional, Dict, Any

from ..domain.ports.llm_port import LLMPort
from ..domain.services.chat_service import ChatService
from ..domain.services.tool_service import ToolService, get_tool_service

logger = logging.getLogger(__name__)


class AIServiceContainer:
    """Container for AI service dependencies."""

    def __init__(self):
        self._llm_adapters: Dict[str, LLMPort] = {}
        self._chat_service: Optional[ChatService] = None
        self._tool_service: Optional[ToolService] = None
        self._default_provider: str = os.environ.get("LLM_PROVIDER", "openrouter")

    def register_adapter(self, name: str, adapter: LLMPort) -> None:
        """Register an LLM adapter."""
        self._llm_adapters[name] = adapter
        logger.info(f"Registered LLM adapter: {name}")

    def get_adapter(self, name: str = None) -> Optional[LLMPort]:
        """Get an LLM adapter by name."""
        name = name or self._default_provider
        return self._llm_adapters.get(name)

    def set_default_provider(self, name: str) -> None:
        """Set the default LLM provider."""
        self._default_provider = name
        if name not in self._llm_adapters:
            logger.warning(f"Provider {name} not registered")

    def get_tool_service(self) -> ToolService:
        """Get or create the tool service."""
        if self._tool_service is None:
            self._tool_service = ToolService()
        return self._tool_service

    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: Dict,
        handler: callable = None,
    ) -> None:
        """Register a tool with the tool service."""
        tool_service = self.get_tool_service()
        tool_service.register_tool(name, description, input_schema, handler)

    def get_chat_service(self, provider: str = None) -> ChatService:
        """Get or create a chat service."""
        adapter = self.get_adapter(provider)

        if adapter is None:
            raise ValueError(f"Adapter not found: {provider or self._default_provider}")

        tool_service = self.get_tool_service()

        return ChatService(
            llm_port=adapter,
            tool_service=tool_service,
        )

    def list_providers(self) -> list:
        """List available providers."""
        return list(self._llm_adapters.keys())


_container: Optional[AIServiceContainer] = None


def get_ai_container() -> AIServiceContainer:
    """Get the global AI service container."""
    global _container
    if _container is None:
        _container = AIServiceContainer()
        _container.register_adapter(
            "openrouter",
            __import__(
                "backend.ai_service.adapters.openrouter_adapter",
                fromlist=["openrouter_adapter"],
            ).openrouter_adapter,
        )
        _container.register_adapter(
            "anthropic",
            __import__(
                "backend.ai_service.adapters.anthropic_adapter",
                fromlist=["anthropic_adapter"],
            ).anthropic_adapter,
        )
        _container.register_adapter(
            "ollama",
            __import__(
                "backend.ai_service.adapters.ollama_adapter",
                fromlist=["ollama_adapter"],
            ).ollama_adapter,
        )
    return _container


def get_llm_adapter(provider: str = None) -> LLMPort:
    """Convenience function to get an LLM adapter."""
    return get_ai_container().get_adapter(provider)


def get_chat_service(provider: str = None) -> ChatService:
    """Convenience function to get a chat service."""
    return get_ai_container().get_chat_service(provider)

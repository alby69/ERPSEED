"""
Adapter Factory for AI Service.

Creates LLM adapter instances based on provider configuration.
"""
import os
from typing import Optional, Dict, Any


class AdapterFactory:
    """Factory for creating LLM adapter instances."""

    _adapters: Dict[str, Any] = {}

    @classmethod
    def get_adapter(cls, provider: Optional[str] = None) -> Any:
        """
        Get an adapter instance for the specified provider.

        Args:
            provider: Provider name (openai, anthropic, ollama, openrouter)

        Returns:
            Adapter instance
        """
        provider = provider or os.environ.get("LLM_PROVIDER", "openrouter")

        if provider in cls._adapters:
            return cls._adapters[provider]

        adapter = cls._create_adapter(provider)
        cls._adapters[provider] = adapter
        return adapter

    @classmethod
    def _create_adapter(cls, provider: str) -> Any:
        """Create a new adapter instance."""
        adapters = {
            "openai": "OpenAIAdapter",
            "anthropic": "AnthropicAdapter",
            "ollama": "OllamaAdapter",
            "openrouter": "OpenRouterAdapter",
        }

        adapter_name = adapters.get(provider, "OpenRouterAdapter")

        try:
            if adapter_name == "OpenAIAdapter":
                from ..adapters.openai_adapter import OpenAIAdapter
                return OpenAIAdapter()
            elif adapter_name == "AnthropicAdapter":
                from ..adapters.anthropic_adapter import AnthropicAdapter
                return AnthropicAdapter()
            elif adapter_name == "OllamaAdapter":
                from ..adapters.ollama_adapter import OllamaAdapter
                return OllamaAdapter()
            elif adapter_name == "OpenRouterAdapter":
                from ..adapters.openrouter_adapter import OpenRouterAdapter
                return OpenRouterAdapter()
        except ImportError as e:
            raise ValueError(f"Failed to load {adapter_name}: {e}")

        raise ValueError(f"Unknown provider: {provider}")

    @classmethod
    def list_providers(cls) -> list:
        """List available providers."""
        return list(set(cls._adapters.keys()))


def get_adapter(provider: Optional[str] = None) -> Any:
    """Convenience function to get adapter."""
    return AdapterFactory.get_adapter(provider)

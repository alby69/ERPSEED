"""
AI Adapters - Supporto per molteplici provider LLM.
"""

from .base import LLMAdapter, LLMResponse, ToolCall, StreamingLLMAdapter
from .openrouter import OpenRouterAdapter, openrouter_adapter
from .anthropic import AnthropicAdapter, anthropic_adapter
from .openai import OpenAIAdapter, openai_adapter
from .ollama import OllamaAdapter, ollama_adapter


def get_adapter(provider: str = None) -> LLMAdapter:
    """
    Factory per ottenere l'adapter corretto.

    Args:
        provider: 'openrouter', 'anthropic', o None per default

    Returns:
        Istanza di LLMAdapter
    """
    if provider is None:
        provider = os.environ.get("LLM_PROVIDER", "openrouter")

    provider = provider.lower()

    if provider == "anthropic":
        return anthropic_adapter
    elif provider == "openrouter":
        return openrouter_adapter
    elif provider == "openai":
        return openai_adapter
    elif provider == "ollama":
        return ollama_adapter
    else:
        raise ValueError(f"Unknown provider: {provider}")


import os

__all__ = [
    "LLMAdapter",
    "LLMResponse",
    "ToolCall",
    "StreamingLLMAdapter",
    "OpenRouterAdapter",
    "AnthropicAdapter",
    "OpenAIAdapter",
    "OllamaAdapter",
    "openrouter_adapter",
    "anthropic_adapter",
    "openai_adapter",
    "ollama_adapter",
    "get_adapter",
]

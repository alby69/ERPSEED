"""
AI LLM Adapters - Infrastructure for LLM providers.
"""
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Iterator

logger = logging.getLogger(__name__)


class LLMResponse:
    def __init__(self, content: str = "", model: str = "", finish_reason: str = ""):
        self.content = content
        self.model = model
        self.finish_reason = finish_reason
        self.tool_calls: List[Dict] = []
        self.has_tool_calls = False
    
    def __repr__(self): return f"LLMResponse(content={self.content[:50]}..., model={self.model})"


class LLMAdapter(ABC):
    name: str = "base"
    supports_streaming: bool = False
    supports_tools: bool = False
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        pass
    
    def stream_chat(self, messages: List[Dict[str, str]], **kwargs) -> Iterator[str]:
        raise NotImplementedError(f"{self.name} does not support streaming")
    
    def _format_tools(self, tools: List[Dict]) -> Any:
        return tools


class OpenRouterAdapter(LLMAdapter):
    name = "openrouter"
    supports_streaming = True
    supports_tools = True
    
    def __init__(self, api_key: str, model: str = "anthropic/claude-3-haiku"):
        self.api_key = api_key
        self.model = model
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        response = LLMResponse(content="OpenRouter response (mock)", model=self.model)
        return response


class OllamaAdapter(LLMAdapter):
    name = "ollama"
    supports_streaming = True
    supports_tools = False
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url
        self.model = model
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        response = LLMResponse(content="Ollama response (mock)", model=self.model)
        return response


class AnthropicAdapter(LLMAdapter):
    name = "anthropic"
    supports_streaming = True
    supports_tools = True
    
    def __init__(self, api_key: str, model: str = "claude-3-haiku-20240307"):
        self.api_key = api_key
        self.model = model
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        response = LLMResponse(content="Anthropic response (mock)", model=self.model)
        return response


ADAPTER_REGISTRY = {
    "openrouter": OpenRouterAdapter,
    "ollama": OllamaAdapter,
    "anthropic": AnthropicAdapter,
}


def get_adapter(provider: str, **config) -> LLMAdapter:
    adapter_class = ADAPTER_REGISTRY.get(provider.lower())
    if not adapter_class:
        raise ValueError(f"Unknown provider: {provider}")
    return adapter_class(**config)

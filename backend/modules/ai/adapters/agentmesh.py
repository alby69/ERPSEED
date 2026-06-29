"""
AgentMesh Adapter for LLM interaction.
This adapter acts as a bridge to the AgentMesh gateway.
"""

from typing import Dict, List, Any
from .base import LLMAdapter, LLMResponse, ToolCall
import logging

logger = logging.getLogger(__name__)

class AgentMeshAdapter(LLMAdapter):
    """
    Adapter for AgentMesh.
    It delegates orchestration and tool selection to the mesh.
    """

    def __init__(self, endpoint: str = None, api_key: str = None):
        self.endpoint = endpoint
        self.api_key = api_key

    @property
    def provider_name(self) -> str:
        return "agentmesh"

    def chat(
        self,
        messages: List[Dict],
        tools: List[Dict] = None,
        model: str = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs
    ) -> LLMResponse:
        """
        In an AgentMesh scenario, this method would call the mesh orchestrator.
        For now, it simulates the integration.
        """
        logger.info(f"Delegating chat to AgentMesh: {messages[-1].get('content')}")

        # Simulate mesh response
        # In a real implementation, we would use requests to call self.endpoint
        return LLMResponse(
            content="I am the AgentMesh orchestrator. I have analyzed your request.",
            raw={"status": "mesh_simulated"}
        )

    def extract_tool_calls(self, response_data: Dict) -> List[ToolCall]:
        """Extracts tool calls from mesh response."""
        # Mesh usually returns a structured list of tasks/tools
        tool_calls = []
        if "tasks" in response_data:
            for task in response_data["tasks"]:
                tool_calls.append(ToolCall(
                    name=task["tool"],
                    arguments=task["args"],
                    tool_id=task.get("id")
                ))
        return tool_calls

    def format_tools(self, tools: List[Dict]) -> List[Dict]:
        """Format tools for AgentMesh (usually OpenAPI/JSON Schema)."""
        return tools

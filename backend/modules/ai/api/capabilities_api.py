"""
Capabilities API - Exposes the AgentMesh Manifest.
"""

from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required
from backend.core.events.capabilities import capability_registry

blp = Blueprint("capabilities", __name__, url_prefix="/api/v1/ai/capabilities", description="Agent Capabilities API")

@blp.route("/")
class CapabilityManifest(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def get(self):
        """
        Get the AgentMesh Manifest (Capability discovery)

        Returns a list of all available agents and their capabilities (tools).
        """
        agents = capability_registry.get_agents()
        manifest = []

        for agent_name in agents:
            capabilities = capability_registry.get_agent_capabilities(agent_name)
            manifest.append({
                "agent": agent_name,
                "capabilities": [c.to_dict() for c in capabilities]
            })

        return {
            "success": True,
            "manifest": manifest,
            "count": len(capability_registry.get_all_capabilities())
        }

@blp.route("/<agent_name>")
class AgentCapabilities(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def get(self, agent_name):
        """Get capabilities for a specific agent."""
        capabilities = capability_registry.get_agent_capabilities(agent_name)
        return {
            "success": True,
            "agent": agent_name,
            "capabilities": [c.to_dict() for c in capabilities]
        }

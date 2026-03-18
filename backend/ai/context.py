"""
AI Context Builder for FlaskERP
Builds context from project schema for RAG injection
"""

import json
import logging
from typing import Dict, Any, List, Optional
from backend.models import db, Project, SysModel, SysField
from backend.builder.models import Block as BlockModel
from backend.models.workflow import Workflow

logger = logging.getLogger(__name__)


class AIContextBuilder:
    """Build context from FlaskERP project for AI context injection"""

    def __init__(self, project_id: int):
        self.project_id = project_id

    def build_context(self) -> str:
        """
        Build comprehensive context from project schema

        Returns:
            Formatted context string for AI system prompt
        """
        context_parts = []

        context_parts.append(self._get_project_info())
        context_parts.append(self._get_models_info())
        context_parts.append(self._get_blocks_info())
        context_parts.append(self._get_workflows_info())

        return "\n\n".join(filter(None, context_parts))

    def _get_project_info(self) -> str:
        """Get basic project information"""
        project = Project.query.get(self.project_id)
        if not project:
            return ""

        info = f"""PROJECT INFO:
- Name: {project.name}
- Title: {project.title}
- Description: {project.description or "No description"}
- ID: {project.id}"""

        return info

    def _get_models_info(self) -> str:
        """Get all models and their fields"""
        models = SysModel.query.filter_by(
            project_id=self.project_id, status="published"
        ).all()

        if not models:
            return "MODELS: No published models in this project yet."

        models_info = ["MODELS EXISTING IN PROJECT:"]

        for model in models:
            model_desc = f"\n### {model.title or model.name} ({model.name})"
            if model.description:
                model_desc += f"\n   Description: {model.description}"

            model_desc += "\n   Fields:"

            if model.fields:
                for field in model.fields:
                    field_info = f"\n     - {field.name} ({field.type})"
                    if field.title and field.title != field.name:
                        field_info += f": {field.title}"
                    if field.required:
                        field_info += " [REQUIRED]"
                    if field.is_unique:
                        field_info += " [UNIQUE]"

                    if field.options:
                        try:
                            opts = (
                                json.loads(field.options)
                                if isinstance(field.options, str)
                                else field.options
                            )
                            if field.type == "select" and "options" in opts:
                                field_info += (
                                    f" | Options: {', '.join(opts['options'])}"
                                )
                            elif field.type == "relation" and "target_table" in opts:
                                field_info += f" | Related to: {opts['target_table']}"
                        except:
                            pass

                    model_desc += field_info
            else:
                model_desc += "\n     (no fields defined)"

            models_info.append(model_desc)

        return "\n".join(models_info)

    def _get_blocks_info(self) -> str:
        """Get available UI blocks"""
        blocks = BlockModel.query.filter_by(project_id=self.project_id).all()

        if not blocks:
            return "\n\nBLOCKS: No custom blocks created yet."

        blocks_info = ["\n\nBLOCKS AVAILABLE:"]

        for block in blocks:
            block_desc = f"\n- {block.name}"
            if block.title:
                block_desc += f": {block.title}"
            if block.block_type:
                block_desc += f" (type: {block.block_type})"

            blocks_info.append(block_desc)

        return "\n".join(blocks_info)

    def _get_workflows_info(self) -> str:
        """Get existing workflows"""
        workflows = Workflow.query.filter_by(project_id=self.project_id).all()

        if not workflows:
            return "\n\nWORKFLOWS: No workflows created yet."

        wf_info = ["\n\nWORKFLOWS:"]

        for wf in workflows:
            wf_desc = f"\n- {wf.name}"
            if wf.description:
                wf_desc += f": {wf.description}"
            wf_desc += f" | Status: {wf.status}"

            wf_info.append(wf_desc)

        return "\n".join(wf_info)

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of project for quick reference"""
        models = SysModel.query.filter_by(
            project_id=self.project_id, status="published"
        ).count()

        blocks = BlockModel.query.filter_by(project_id=self.project_id).count()

        workflows = Workflow.query.filter_by(project_id=self.project_id).count()

        return {
            "project_id": self.project_id,
            "models_count": models,
            "blocks_count": blocks,
            "workflows_count": workflows,
        }


def get_project_context(project_id: int) -> str:
    """
    Convenience function to get project context

    Args:
        project_id: ID of the project

    Returns:
        Formatted context string
    """
    builder = AIContextBuilder(project_id)
    return builder.build_context()


def get_conversation_context(project_id: int, limit: int = 5) -> str:
    """
    Get recent conversation context for learning

    Args:
        project_id: ID of the project
        limit: Number of recent conversations to include

    Returns:
        Formatted context from recent conversations
    """
    try:
        from backend.models import AIConversation

        conversations = (
            AIConversation.query.filter_by(project_id=project_id, was_successful=True)
            .order_by(AIConversation.created_at.desc())
            .limit(limit)
            .all()
        )

        if not conversations:
            return ""

        context = "\n\nPREVIOUS SUCCESSFUL CONVERSATIONS (for reference):"

        for conv in reversed(conversations):  # Oldest first
            context += f"\n\nUser asked: {conv.user_message[:200]}"
            if conv.ai_response:
                # Extract action summary from response
                context += f"\nAI responded with: {conv.ai_response[:200]}"

        return context

    except Exception as e:
        logger.warning(f"Could not load conversation context: {e}")
        return ""

import logging
from backend.modules.ai.service import AIService
from backend.models import AIConversation, db
from backend.modules.ai.context import get_project_context

logger = logging.getLogger(__name__)

class AICommandHandler:
    def __init__(self):
        self.ai_service = AIService()

    def handle_generate_config(self, cmd):
        return self.ai_service.generate_erp_config(
            user_request=cmd.user_request,
            projectId=cmd.projectId,
            userId=cmd.userId,
            apply_directly=cmd.apply_directly
        )

    def handle_save_conversation(self, cmd):
        try:
            conversation = AIConversation(
                projectId=cmd.projectId,
                userId=cmd.userId,
                user_message=cmd.user_message,
                ai_response=cmd.ai_response[:5000] if cmd.ai_response else None,
                was_successful=cmd.was_successful,
                user_correction=cmd.user_correction,
                action_taken=cmd.action_taken,
                context_snapshot=get_project_context(cmd.projectId),
            )
            db.session.add(conversation)
            db.session.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            return False

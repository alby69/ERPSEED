from backend.extensions import db
from backend.core.models.base import BaseModel


class AIConversation(BaseModel):
    """
    Stores AI conversations for learning and context.
    Enables the AI to learn from previous interactions.
    """

    __tablename__ = "ai_conversations"

    projectId = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    user_message = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text)

    was_successful = db.Column(db.Boolean, default=False)
    user_correction = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Integer, nullable=True)

    action_taken = db.Column(
        db.String(50)
    )
    entities_created = db.Column(db.JSON)

    context_snapshot = db.Column(db.Text)

    project = db.relationship("Project")
    user = db.relationship("User")

    def __repr__(self):
        return f"<AIConversation project={self.projectId} user={self.userId}>"

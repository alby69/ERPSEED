"""
Wizard Session Models.
"""
from backend.extensions import db
from backend.core.models.base import BaseModel
from backend.core.models.mixins import CoreEntityMixin


class WizardSession(BaseModel, CoreEntityMixin):
    """
    Stores a Guided ERP Wizard session state.
    """
    __tablename__ = "wizard_sessions"

    session_name = db.Column(db.String(150), nullable=False, default="Nuovo Wizard ERP")
    industry = db.Column(db.String(100), nullable=True)
    answers = db.Column(db.JSON, nullable=True, comment="Structured user answers from questionnaire")
    domain_spec = db.Column(db.JSON, nullable=True, comment="Parsed ER schema & domain specs")
    status = db.Column(db.String(30), nullable=False, default="draft")  # draft, analyzed, provisioned

    def __repr__(self):
        return f"<WizardSession {self.id}:{self.session_name} ({self.status})>"

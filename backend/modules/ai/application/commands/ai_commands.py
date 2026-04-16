from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class GenerateConfigCommand:
    user_request: str
    project_id: int
    user_id: Optional[int] = None
    apply_directly: bool = False

@dataclass
class SaveConversationCommand:
    project_id: int
    user_id: int
    user_message: str
    ai_response: str
    was_successful: bool = False
    user_correction: Optional[str] = None
    action_taken: Optional[str] = None

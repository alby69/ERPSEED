from backend.modules.projects.api.rest_api import blp as projects_bp
from backend.modules.analytics.api.dashboard_api import blp as dashboard_bp
from backend.modules.analytics.api.rest_api import blp as analytics_bp
from backend.modules.dynamic_api.api.rest_api import blp as dynamic_api_bp
from backend.modules.system_tools.api.templates_api import blp as template_bp
from backend.modules.system_tools.api.visual_builder_api import blp as visual_builder_bp
from backend.modules.system_tools.api.versioning_api import blp as versioning_bp
from backend.modules.system_tools.api.debugging_api import blp as debugging_bp
from backend.modules.system_tools.api.gdo_api import blp as gdo_reconciliation_bp
from backend.modules.automation.api.workflows_api import blp as workflows_bp
from backend.modules.automation.api.webhooks_api import blp as webhooks_bp

__all__ = [
    "projects_bp",
    "dashboard_bp",
    "analytics_bp",
    "dynamic_api_bp",
    "template_bp",
    "visual_builder_bp",
    "versioning_bp",
    "debugging_bp",
    "gdo_reconciliation_bp",
    "workflows_bp",
    "webhooks_bp",
]

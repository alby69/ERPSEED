from flask_smorest import Blueprint
from .routes.dynamic_list import register_list_routes
from .routes.dynamic_item import register_item_routes
from .routes.dynamic_meta import register_meta_routes
from .routes.dynamic_io import register_io_routes
from .routes.audit import register_audit_routes

blp = Blueprint(
    "dynamic_api",
    __name__,
    url_prefix="/api/v1/projects/<int:projectId>",
    description="Dynamic CRUD API for builder models"
)

# Register routes
register_list_routes(blp)
register_item_routes(blp)
register_meta_routes(blp)
register_io_routes(blp)
register_audit_routes(blp)

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required

blp = Blueprint("visual_builder", __name__, description="Visual Drag-and-Drop Builder API")

@blp.route("/visual-builder/views/<int:view_id>")
class VisualBuilderView(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def get(self, view_id):
        """Get visual configuration for a view"""
        return {"id": view_id, "layout": []}

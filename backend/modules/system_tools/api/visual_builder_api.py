from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required

blp = Blueprint("visual_builder", __name__, description="Visual Drag-and-Drop Builder API")

@blp.route("/visual-builder/views/<int:viewId>")
class VisualBuilderView(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def get(self, viewId):
        """Get visual configuration for a view"""
        return {"id": viewId, "layout": []}

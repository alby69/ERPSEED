from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required

blp = Blueprint("visual_builder", __name__, description="Visual Drag-and-Drop Builder API")

from backend.models.system import SysView
from backend.extensions import db
from marshmallow import Schema, fields

class ViewLayoutSchema(Schema):
    layout = fields.List(fields.Dict(), required=True)

@blp.route("/visual-builder/views/<int:viewId>")
class VisualBuilderView(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def get(self, viewId):
        """Get visual configuration for a view"""
        view = SysView.query.get_or_404(viewId)
        return {"id": view.id, "layout": view.get_layout()}

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(ViewLayoutSchema)
    @blp.response(200)
    def put(self, data, viewId):
        """Save visual configuration for a view"""
        view = SysView.query.get_or_404(viewId)
        view.set_layout(data['layout'])
        db.session.commit()
        return {"message": "Layout saved successfully"}

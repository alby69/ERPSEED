from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required

blp = Blueprint("gdo", __name__, description="GDO Reconciliation Tool")

@blp.route("/gdo/sessions")
class GDOSessionList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """List GDO sessions"""
        return []

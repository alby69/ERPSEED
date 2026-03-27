from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required

blp = Blueprint("debugging", __name__, description="System health and debugging")

@blp.route("/health")
class HealthCheck(MethodView):
    def get(self):
        """System health check"""
        return {"status": "ok"}

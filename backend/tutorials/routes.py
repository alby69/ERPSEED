"""
API endpoint per tutorial dei moduli.
Serve file markdown dal directory tutorials/.
"""
import os
from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint

tutorial_blp = Blueprint(
    "tutorials", __name__, url_prefix="/api/v1/tutorials",
    description="Tutorial dei moduli"
)

TUTORIALS_DIR = os.path.join(os.path.dirname(__file__))


@tutorial_blp.route("/<string:module_name>")
class TutorialView(MethodView):
    def get(self, module_name):
        safe_name = module_name.replace("..", "").replace("/", "")
        filepath = os.path.join(TUTORIALS_DIR, f"{safe_name}.md")
        if not os.path.exists(filepath):
            return jsonify({"error": "Tutorial not found"}), 404
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return jsonify({"content": content, "module": safe_name})

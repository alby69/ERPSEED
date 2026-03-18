"""
ERPSEED Core API - REST API without authentication

This API provides endpoints for managing ERP systems.
Authentication should be handled by a separate auth module.
"""

from flask import Flask, jsonify, request
from typing import Dict, Any, Optional

from .builder import ModelBuilder, BlockBuilder, WorkflowBuilder, BusinessRuleBuilder
from .generator import export_project, export_model, export_block
from .parser import parse_spec_file
from .schemas import validate_against_schema


def create_app(instance_name: str = "default") -> Flask:
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config["INSTANCE_NAME"] = instance_name
    
    model_builder = ModelBuilder()
    block_builder = BlockBuilder()
    workflow_builder = WorkflowBuilder()
    business_rule_builder = BusinessRuleBuilder()
    
    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "healthy", "instance": instance_name})
    
    @app.route("/api/projects", methods=["GET"])
    def list_projects():
        return jsonify({"projects": []})
    
    @app.route("/api/projects", methods=["POST"])
    def create_project():
        data = request.get_json()
        return jsonify({"project": data}), 201
    
    @app.route("/api/projects/<project_id>", methods=["GET"])
    def get_project(project_id):
        return jsonify({"id": project_id, "name": "Project"})
    
    @app.route("/api/projects/<project_id>", methods=["PUT"])
    def update_project(project_id):
        data = request.get_json()
        return jsonify({"id": project_id, "updated": True})
    
    @app.route("/api/projects/<project_id>", methods=["DELETE"])
    def delete_project(project_id):
        return jsonify({"deleted": True})
    
    @app.route("/api/models", methods=["GET"])
    def list_models():
        return jsonify({"models": []})
    
    @app.route("/api/models", methods=["POST"])
    def create_model():
        data = request.get_json()
        model_builder.build(data)
        return jsonify({"model": data}), 201
    
    @app.route("/api/models/<model_id>", methods=["GET"])
    def get_model(model_id):
        return jsonify({"id": model_id})
    
    @app.route("/api/models/<model_id>", methods=["PUT"])
    def update_model(model_id):
        data = request.get_json()
        model_builder.build(data)
        return jsonify({"id": model_id, "updated": True})
    
    @app.route("/api/models/<model_id>", methods=["DELETE"])
    def delete_model(model_id):
        return jsonify({"deleted": True})
    
    @app.route("/api/blocks", methods=["GET"])
    def list_blocks():
        return jsonify({"blocks": []})
    
    @app.route("/api/blocks", methods=["POST"])
    def create_block():
        data = request.get_json()
        block_builder.build(data)
        return jsonify({"block": data}), 201
    
    @app.route("/api/blocks/<block_id>", methods=["GET"])
    def get_block(block_id):
        return jsonify({"id": block_id})
    
    @app.route("/api/workflows", methods=["GET"])
    def list_workflows():
        return jsonify({"workflows": []})
    
    @app.route("/api/workflows", methods=["POST"])
    def create_workflow():
        data = request.get_json()
        workflow_builder.build(data)
        return jsonify({"workflow": data}), 201
    
    @app.route("/api/business-rules", methods=["GET"])
    def list_business_rules():
        return jsonify({"business_rules": []})
    
    @app.route("/api/business-rules", methods=["POST"])
    def create_business_rule():
        data = request.get_json()
        business_rule_builder.build(data)
        return jsonify({"business_rule": data}), 201
    
    @app.route("/api/export", methods=["POST"])
    def export():
        data = request.get_json()
        project_path = data.get("project_path")
        if not project_path:
            return jsonify({"error": "project_path required"}), 400
        result = export_project(project_path)
        return jsonify(result)
    
    @app.route("/api/validate", methods=["POST"])
    def validate():
        data = request.get_json()
        schema_type = data.get("schema")
        json_data = data.get("data")
        if not schema_type or not json_data:
            return jsonify({"error": "schema and data required"}), 400
        is_valid, errors = validate_against_schema(json_data, schema_type)
        return jsonify({"valid": is_valid, "errors": errors})
    
    @app.route("/api/parse", methods=["POST"])
    def parse():
        if "file" not in request.files:
            return jsonify({"error": "file required"}), 400
        file = request.files["file"]
        result = parse_spec_file(file)
        return jsonify(result)
    
    return app


def register_blueprint(flask_app: Flask, instance_name: str = "default"):
    """Register ERPSEED Core blueprint to existing Flask app"""
    core_app = create_app(instance_name)
    
    for rule in core_app.url_map.iter_rules():
        if rule.endpoint != "static":
            view_func = core_app.view_functions[rule.endpoint]
            flask_app.add_url_rule(
                rule.rule,
                view_func=view_func,
                methods=rule.methods - {"HEAD", "OPTIONS"}
            )

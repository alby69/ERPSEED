"""
Wizard REST API Endpoints.
"""
from flask import request, jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.extensions import db
from backend.modules.wizard.models import WizardSession
from backend.modules.wizard.schemas import (
    WizardSessionSchema,
    DomainAnalysisRequestSchema,
    ProvisionDomainRequestSchema
)
from backend.modules.wizard.services import (
    domain_analysis_service,
    wizard_provisioning_service
)

blp = Blueprint(
    "wizard",
    __name__,
    url_prefix="/api/v1/wizard",
    description="Guided ERP Domain Wizard APIs"
)


@blp.route("/analyze-domain", methods=["POST"])
@jwt_required()
@blp.arguments(DomainAnalysisRequestSchema)
def analyze_domain(data):
    """Analyzes questionnaire and custom description to build candidate ERP entities."""
    try:
        spec = domain_analysis_service.analyze_domain(data)
        return jsonify(spec), 200
    except Exception as e:
        abort(500, message=f"Failed to analyze domain: {str(e)}")


@blp.route("/provision", methods=["POST"])
@jwt_required()
@blp.arguments(ProvisionDomainRequestSchema)
def provision_domain(data):
    """Provisions SQLAlchemy models and metadata based on final domain specification."""
    user = get_jwt_identity() or {}
    tenant_id = user.get("tenant_id", 1) if isinstance(user, dict) else 1
    project_id = data.get("project_id", 1)
    domain_spec = data.get("domain_spec", {})

    try:
        result = wizard_provisioning_service.provision_domain(
            domain_spec,
            project_id=project_id,
            tenant_id=tenant_id
        )

        session_id = data.get("session_id")
        if session_id:
            session = WizardSession.query.filter_by(id=session_id, tenant_id=tenant_id).first()
            if session:
                session.status = "provisioned"
                session.domain_spec = domain_spec
                db.session.commit()

        return jsonify(result), 200
    except Exception as e:
        abort(500, message=f"Provisioning failed: {str(e)}")


@blp.route("/sessions", methods=["GET"])
@jwt_required()
@blp.response(200, WizardSessionSchema(many=True))
def list_sessions():
    """Lists wizard sessions for tenant."""
    user = get_jwt_identity() or {}
    tenant_id = user.get("tenant_id", 1) if isinstance(user, dict) else 1
    return WizardSession.query.filter_by(tenant_id=tenant_id).all()


@blp.route("/sessions", methods=["POST"])
@jwt_required()
@blp.response(201, WizardSessionSchema)
def create_session():
    """Creates a new wizard session."""
    user = get_jwt_identity() or {}
    tenant_id = user.get("tenant_id", 1) if isinstance(user, dict) else 1
    data = request.get_json() or {}

    session = WizardSession(
        tenant_id=tenant_id,
        session_name=data.get("session_name", "Nuovo Wizard ERP"),
        industry=data.get("industry", "Generico"),
        answers=data.get("answers", {}),
        status="draft"
    )
    db.session.add(session)
    db.session.commit()
    return session

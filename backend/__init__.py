import os
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from .extensions import db, socketio, api

# Import Blueprints
from .auth import auth_bp
from .users import blp as users_bp
from .parties import blp as parties_bp
from .products import blp as products_bp
from .projects import blp as projects_bp
from .sales import blp as sales_bp
from .builder import blp as builder_bp
from .analytics import blp as analytics_bp
from .dynamic_api import blp as dynamic_api_bp

def create_app(db_url=None):
    app = Flask(__name__)

    # --- Configuration ---
    app.config["API_TITLE"] = "FlaskERP API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "a-silly-default-secret-key-for-dev")
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]

    # --- Initialize Extensions ---
    db.init_app(app)
    api.init_app(app)
    jwt = JWTManager(app)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"message": "The token has expired.", "error": "token_expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"message": "Signature verification failed.", "error": "invalid_token"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            "description": "Request does not contain an access token.",
            "error": "authorization_required"
        }), 401

    socketio.init_app(app, cors_allowed_origins="*")
    
    # --- CORS Configuration ---
    # This allows the frontend at localhost:5173 to make requests to the backend.
    CORS(app, resources={r"/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "expose_headers": ["X-Total-Count", "X-Pages", "X-Current-Page", "X-Per-Page", "Content-Range"],
        "supports_credentials": True
    }})

    # --- Global Error Handler ---
    @app.errorhandler(Exception)
    def handle_exception(e):
        # Pass through HTTP errors
        if isinstance(e, HTTPException):
            return e
        # Log and return JSON for 500 errors
        import traceback
        print(traceback.format_exc())
        return jsonify({"message": "Internal Server Error", "error": str(e)}), 500

    # --- Database Creation ---
    with app.app_context():
        # Import models to ensure they are registered with SQLAlchemy
        from . import models
        db.create_all()

    # --- Register Blueprints ---
    api.register_blueprint(auth_bp)
    api.register_blueprint(users_bp)
    api.register_blueprint(parties_bp)
    api.register_blueprint(products_bp)
    api.register_blueprint(projects_bp)
    api.register_blueprint(sales_bp)
    api.register_blueprint(builder_bp)
    api.register_blueprint(analytics_bp)
    api.register_blueprint(dynamic_api_bp)

    return app
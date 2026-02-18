import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_babel import Babel, gettext as _
from werkzeug.exceptions import HTTPException

from .extensions import db, socketio, api, jwt, ma, migrate

# Import Core Middleware
from .core.middleware.tenant_middleware import TenantMiddleware
from .core.services.query_filter import TenantQueryFilter, SoftDeleteFilter

# Import Blueprints
from .auth import auth_bp
from .users import blp as users_bp
from .parties import blp as parties_bp
from .products import blp as products_bp
from .projects import blp as projects_bp
from .sales import blp as sales_bp
from .purchases import blp as purchases_bp
from .dashboard import blp as dashboard_bp
from .builder import blp as builder_bp
from .analytics import blp as analytics_bp
from .dynamic_api import blp as dynamic_api_bp
from .webhook_routes import blp as webhooks_bp
from .workflow_routes import blp as workflows_bp

# Import plugins
from .plugins import PluginRegistry
from .plugins.accounting.plugin import get_plugin as get_accounting_plugin
from .plugins.hr.plugin import get_plugin as get_hr_plugin
from .plugins.inventory.plugin import get_plugin as get_inventory_plugin

# Import Core API blueprints
from .core.api.auth import auth_bp as core_auth_bp
from .core.api.tenant import tenant_bp


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
    migrate.init_app(app, db)
    api.init_app(app)
    jwt.init_app(app)
    ma.init_app(app)
    
    # --- Initialize Multi-tenant Filters ---
    TenantQueryFilter.init_app(app)
    SoftDeleteFilter.init_app(app)
    
    # --- Initialize Tenant Middleware ---
    TenantMiddleware.init_app(app)
    
    # --- Initialize Babel ---
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
    
    def get_locale():
        # Get language from header Accept-Language
        return request.accept_languages.best_match(['en', 'it']) if request.accept_languages else 'en'
    
    babel = Babel(app, locale_selector=get_locale)

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
    CORS(app, resources={r"/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173", "http://0.0.0.0:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
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

    # --- Register Blueprints ---
    # Core API con Marshmallow (nuovo)
    api.register_blueprint(core_auth_bp, url_prefix='/api/v1/auth')
    api.register_blueprint(tenant_bp, url_prefix='/api/v1/tenant')
    
    # Vecchi blueprint per retrocompatibilità frontend - rinominati per evitare conflitti
    api.register_blueprint(auth_bp, name='legacy_auth')  # /login, /me, etc.
    api.register_blueprint(users_bp)
    api.register_blueprint(parties_bp)
    api.register_blueprint(products_bp)
    api.register_blueprint(projects_bp)
    api.register_blueprint(sales_bp)
    api.register_blueprint(purchases_bp)
    api.register_blueprint(dashboard_bp)
    api.register_blueprint(builder_bp)
    api.register_blueprint(analytics_bp)
    api.register_blueprint(dynamic_api_bp)
    api.register_blueprint(webhooks_bp)
    api.register_blueprint(workflows_bp)

    # --- Initialize Plugins ---
    _init_plugins(app, api, db)

    return app


def _init_plugins(app, api, db):
    """Initialize and register plugins."""
    # Register plugins
    PluginRegistry.register(get_accounting_plugin())
    PluginRegistry.register(get_hr_plugin())
    PluginRegistry.register(get_inventory_plugin())
    
    # Enable plugins
    try:
        PluginRegistry.enable('accounting', app=app, db=db, api=api)
        PluginRegistry.enable('hr', app=app, db=db, api=api)
        PluginRegistry.enable('inventory', app=app, db=db, api=api)
    except Exception as e:
        print(f"Warning: Could not enable some plugins: {e}")
import os
from typing import Any
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_babel import Babel, gettext as _
from werkzeug.exceptions import HTTPException
from flask.json.provider import DefaultJSONProvider
import decimal

from .extensions import db, socketio, api, jwt, ma, migrate

# Import Core Middleware
from .core.middleware.tenant_middleware import TenantMiddleware
from .core.services.query_filter import TenantQueryFilter, SoftDeleteFilter

# Import Blueprints
from .auth import auth_bp
from .users import blp as users_bp
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
from .plugins import ModuleRegistry, PluginRegistry
from .plugins.accounting.plugin import get_plugin as get_accounting_plugin
from .plugins.hr.plugin import get_plugin as get_hr_plugin
from .plugins.inventory.plugin import get_plugin as get_inventory_plugin

# Import Core API blueprints
from .core.api.auth import auth_bp as core_auth_bp
from .core.api.tenant import tenant_bp
from .core.api.modules import blp as modules_bp
from .core.api.system import blp as system_bp
from .core.api.pdf import pdf_bp
from .core.api.test_runner import blp as test_runner_bp
from .core.api.custom_modules import blp as custom_modules_bp
from .core.api.module_api import blp as module_api_bp
from .core.api.import_export import blp as import_export_bp

# Import Entities (Vision Archetypes)
from .entities.routes import soggetto_blp, ruolo_blp, indirizzo_blp, contatto_blp
from .entities.indirizzo_geografico import geografico_blp
from .entities.comuni_routes import comuni_blp

# Import Builder Models (Archetype, Component, Block)
from .builder.models import (
    Archetype,
    Component,
    Block,
    BlockRelationship,
    create_system_archetypes,
)

# Import Marketplace Models
from .marketplace.models import (
    Category,
    BlockListing,
    Review,
    PaymentTransaction,
    Author,
    create_default_categories,
)

# Import Builder API
from .builder.api import blp as builder_api_blp

# Import Marketplace API
from .marketplace.api import blp as marketplace_api_blp

# Import AI Assistant API
from .ai.api import blp as ai_bp

# Import Visual Builder API
from .visual_builder_api import blp as visual_builder_bp

# Import Template API
from .template_api import blp as template_bp


class CustomJSONProvider(DefaultJSONProvider):
    def default(self, o: Any) -> Any:
        if isinstance(o, decimal.Decimal):
            return float(o)
        if callable(o):
            import logging
            logging.getLogger(__name__).error(f"JSON serialization error: callable type={type(o)}, obj={o}")
            return str(o)
        return super().default(o)

def create_app(db_url=None):
    # Configure Marshmallow schema name resolver to avoid name conflicts in OpenAPI spec
    def schema_name_resolver(schema):
        # Strettamente basato sul suggerimento della chat per risolvere i warning di apispec
        cls_name = schema.__class__.__name__
        module_name = getattr(schema, "__module__", "common").split(".")[-1]

        # Se il nome finisce con Schema lo togliamo per pulizia nel generare l'OpenAPI
        if cls_name.endswith("Schema"):
            display_name = cls_name[:-6]
        else:
            display_name = cls_name

        # Nome unico: Classe + Modulo (es. AuthResponse_auth)
        return f"{display_name}_{module_name}"

    app = Flask(__name__)

    # --- Configuration ---
    app.config["API_TITLE"] = "FlaskERP API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = (
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv(
        "DATABASE_URL", "sqlite:///data.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["JWT_SECRET_KEY"] = os.getenv(
        "JWT_SECRET_KEY", "a-silly-default-secret-key-for-dev"
    )
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]

    # --- Custom JSON Provider ---
    app.json_provider_class = CustomJSONProvider
    app.json = app.json_provider_class(app)

    # --- Initialize Extensions ---
    db.init_app(app)
    migrate.init_app(app, db)

    api.init_app(app)

    # Configure Marshmallow schema name resolver AFTER api.init_app to avoid serialization in spec
    spec = getattr(api, 'spec', None)
    if spec is not None:
        plugins = getattr(spec, 'plugins', None)
        if plugins is not None:
            for plugin in plugins:
                if hasattr(plugin, 'schema_name_resolver'):
                    plugin.schema_name_resolver = schema_name_resolver
                    break

    jwt.init_app(app)
    ma.init_app(app)

    # Create test tables if they don't exist
    with app.app_context():
        from backend.core.models.test_models import (
            TestSuite,
            TestCase,
            TestExecution,
            ModuleStatusHistory,
        )

        db.create_all()

        # Add missing columns to existing tables using a cross-compatible way (SQLAlchemy inspector)
        from sqlalchemy import inspect, text

        def add_column_if_not_exists(table_name, column_name, column_type):
            try:
                inspector = inspect(db.engine)
                if table_name not in inspector.get_table_names():
                    return

                columns = [c['name'] for c in inspector.get_columns(table_name)]
                if column_name not in columns:
                    db.session.execute(
                        text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
                    )
                    db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error adding {table_name}.{column_name}: {e}")

        with app.app_context():
            add_column_if_not_exists('sys_dashboards', 'updated_at', 'TIMESTAMP')
            add_column_if_not_exists('sys_models', 'updated_at', 'TIMESTAMP')
            add_column_if_not_exists('sys_fields', 'created_at', 'TIMESTAMP')
            add_column_if_not_exists('sys_fields', 'updated_at', 'TIMESTAMP')

    # --- Initialize Multi-tenant Filters ---
    TenantQueryFilter.init_app(app)
    SoftDeleteFilter.init_app(app)

    # --- Initialize Tenant Middleware ---
    TenantMiddleware.init_app(app)

    # --- Initialize Babel ---
    app.config["BABEL_TRANSLATION_DIRECTORIES"] = "translations"

    def get_locale():
        # Get language from header Accept-Language
        return (
            request.accept_languages.best_match(["en", "it"])
            if request.accept_languages
            else "en"
        )

    babel = Babel(app, locale_selector=get_locale)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify(
            {"message": "The token has expired.", "error": "token_expired"}
        ), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify(
            {"message": "Signature verification failed.", "error": "invalid_token"}
        ), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify(
            {
                "description": "Request does not contain an access token.",
                "error": "authorization_required",
            }
        ), 401

    socketio.init_app(app, cors_allowed_origins="*")

    # --- CORS Configuration ---
    CORS(
        app,
        resources={
            r"/*": {
                "origins": [
                    "http://localhost:5173",
                    "http://127.0.0.1:5173",
                    "http://0.0.0.0:5173",
                ],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
                "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                "expose_headers": [
                    "X-Total-Count",
                    "X-Pages",
                    "X-Current-Page",
                    "X-Per-Page",
                    "Content-Range",
                ],
                "supports_credentials": True,
            }
        },
    )


    # --- Global Error Handler ---
    @app.errorhandler(Exception)
    def handle_exception(e):
        # Pass through HTTP errors
        if isinstance(e, HTTPException):
            return jsonify({
                "code": e.code,
                "name": e.name,
                "description": e.description,
            }), e.code or 500
        # Log and return JSON for 500 errors
        import traceback

        print(traceback.format_exc())
        return jsonify({"message": "Internal Server Error", "error": str(e)}), 500

    # --- Register Blueprints ---
    # Core API con Marshmallow (nuovo)
    api.register_blueprint(core_auth_bp, url_prefix="/api/v1/auth")
    api.register_blueprint(tenant_bp, url_prefix="/api/v1/tenant")
    api.register_blueprint(modules_bp)
    api.register_blueprint(system_bp)
    api.register_blueprint(pdf_bp)
    api.register_blueprint(test_runner_bp)

    # Vecchi blueprint per retrocompatibilità frontend - rinominati per evitare conflitti
    api.register_blueprint(auth_bp, name="legacy_auth")  # /login, /me, etc.
    api.register_blueprint(users_bp)
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
    api.register_blueprint(builder_api_blp)
    api.register_blueprint(marketplace_api_blp)
    api.register_blueprint(ai_bp)
    api.register_blueprint(visual_builder_bp)
    api.register_blueprint(template_bp)
    # api.register_blueprint(versioning_bp) # Assuming these are not ready yet
    # api.register_blueprint(debugging_bp)
    api.register_blueprint(custom_modules_bp)
    api.register_blueprint(module_api_bp)
    api.register_blueprint(import_export_bp)

    # Vision Entities (Archetypes)
    api.register_blueprint(soggetto_blp, url_prefix="/api/v1")
    api.register_blueprint(ruolo_blp, url_prefix="/api/v1")
    api.register_blueprint(indirizzo_blp, url_prefix="/api/v1")
    api.register_blueprint(contatto_blp, url_prefix="/api/v1")
    api.register_blueprint(geografico_blp)
    api.register_blueprint(comuni_blp)

    # --- Initialize Plugins ---
    _init_plugins(app, api, db)

    return app


def _init_plugins(app, api, db):
    """Initialize and register plugins."""
    # Register plugins
    ModuleRegistry.register(get_accounting_plugin())
    ModuleRegistry.register(get_hr_plugin())
    ModuleRegistry.register(get_inventory_plugin())

    # Enable plugins
    try:
        ModuleRegistry.enable("accounting", app=app, db=db, api=api)
        ModuleRegistry.enable("hr", app=app, db=db, api=api)
        ModuleRegistry.enable("inventory", app=app, db=db, api=api)
    except Exception as e:
        print(f"Warning: Could not enable some plugins: {e}")

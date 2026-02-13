from flask import Flask, send_from_directory
from flask_smorest import Api
from flask_cors import CORS
from app.config import Config
from app.extensions import db, migrate, jwt, mail

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS to allow requests from the frontend
    CORS(app, expose_headers=["X-Total-Count", "X-Pages", "X-Current-Page", "X-Per-Page"])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    api = Api(app)

    # Import models to ensure they are registered with SQLAlchemy
    from backend import models

    # Register Blueprints
    from app.resources.user import blp as UserBlueprint
    api.register_blueprint(UserBlueprint)
    from app.resources.party import blp as PartyBlueprint
    api.register_blueprint(PartyBlueprint)
    from app.resources.product import blp as ProductBlueprint
    api.register_blueprint(ProductBlueprint)
    from app.resources.sales import blp as SalesBlueprint
    api.register_blueprint(SalesBlueprint)

    # Route to serve uploaded files (images, documents)
    @app.route('/uploads/<path:filename>')
    def serve_uploads(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    @app.route('/')
    def index():
        return {"message": "FlaskERP API is running", "status": "ok"}

    return app
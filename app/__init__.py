from flask import Flask
from flask_login import LoginManager
from app.extensions import db, migrate, login_manager
from config import Config

# Import Blueprints
from app.routes.auth import auth_bp
from app.routes.auth.profile import profile_bp
from app.routes.main import main_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(main_bp)

    return app

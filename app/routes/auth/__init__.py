from flask import Flask
from app.extensions import db, migrate, login_manager
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register Blueprints
    from app.routes.auth.routes import auth_bp
    app.register_blueprint(auth_bp)

    return app

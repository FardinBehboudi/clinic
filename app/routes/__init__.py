from flask import Blueprint
from .main.routes import main_bp

def register_blueprints(app):
    app.register_blueprint(main_bp)

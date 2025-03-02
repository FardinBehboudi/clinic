from flask import Flask
from app.extensions import db, migrate
from config import Config
from app.routes import register_blueprints

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    register_blueprints(app)

    return app

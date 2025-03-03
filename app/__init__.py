from flask import Flask
from flask_login import LoginManager
from app.extensions import db, migrate, login_manager
from config import Config

# Import Blueprints
from app.routes.auth import auth_bp
from app.routes.auth.profile import profile_bp
from app.routes.main import main_bp
from app.routes.patient import patients_bp
from app.routes.clinic import clinics_bp
from app.routes.user import users_bp
from app.routes.role import roles_bp
from app.routes.procedure import procedures_bp
from app.routes.procedure_settings import procedure_settings_bp
from app.routes.operator import operators_bp
from app.routes.operator_shares import operator_shares_bp
from app.routes.operator_earnings import operator_earnings_bp
from app.routes.clinic_income import clinic_income_bp
from app.routes.appointments import appointments_bp
from app.routes.appointment_status import appointment_status_bp
from app.routes.expense_settings import expense_settings_bp
from app.routes.expenses import expenses_bp
from app.routes.inventory import inventory_bp

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
    app.register_blueprint(patients_bp)
    app.register_blueprint(clinics_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(roles_bp)
    app.register_blueprint(procedures_bp)
    app.register_blueprint(procedure_settings_bp)
    app.register_blueprint(operators_bp)
    app.register_blueprint(operator_shares_bp)
    app.register_blueprint(operator_earnings_bp)
    app.register_blueprint(clinic_income_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(appointment_status_bp)
    app.register_blueprint(expense_settings_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(inventory_bp)

    return app

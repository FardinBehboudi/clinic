from flask import Blueprint

expense_settings_bp = Blueprint('expense_settings', __name__, url_prefix='/expense-settings')

from . import routes

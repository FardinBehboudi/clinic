from flask import Blueprint

procedure_settings_bp = Blueprint('procedure_settings', __name__, url_prefix='/procedure-settings')

from . import routes  # Import routes after defining Blueprint

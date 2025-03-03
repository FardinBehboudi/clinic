from flask import Blueprint

clinics_bp = Blueprint('clinics', __name__, url_prefix='/clinics')

from . import routes  # Import routes after defining Blueprint

from flask import Blueprint

operators_bp = Blueprint('operators', __name__, url_prefix='/operators')

from . import routes  # Import routes after defining Blueprint

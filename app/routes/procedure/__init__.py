from flask import Blueprint

procedures_bp = Blueprint('procedures', __name__, url_prefix='/procedures')

from . import routes  # Import routes after defining Blueprint

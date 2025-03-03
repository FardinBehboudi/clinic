from flask import Blueprint

operator_shares_bp = Blueprint('operator_shares', __name__, url_prefix='/operator-shares')

from . import routes

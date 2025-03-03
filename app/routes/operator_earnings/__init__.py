from flask import Blueprint

operator_earnings_bp = Blueprint('operator_earnings', __name__, url_prefix='/operator-earnings')

from . import routes

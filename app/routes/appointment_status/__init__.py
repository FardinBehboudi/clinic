from flask import Blueprint

appointment_status_bp = Blueprint('appointment_status', __name__, url_prefix='/appointment-status')

from . import routes

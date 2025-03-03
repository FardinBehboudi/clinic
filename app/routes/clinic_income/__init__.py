from flask import Blueprint

clinic_income_bp = Blueprint('clinic_income', __name__, url_prefix='/clinic-income')

from . import routes

from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.finance import ClinicIncome
from . import clinic_income_bp
from ...models import Procedure, ProcedureType


# 📌 Ensure Only Admins & Doctors Can View Clinic Income
def clinic_income_access_control(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.role.role_name not in ["Admin", "Doctor"]:
            flash("Access denied: You do not have permission to view clinic income.", "danger")
            return redirect(url_for('dashboard'))
        return func(*args, **kwargs)
    return login_required(wrapper)

# 📌 List Clinic Income (Only Admins & Doctors)
@clinic_income_bp.route('/', methods=['GET'])
@login_required
@clinic_income_access_control
def list_clinic_income():
    procedure_types = ProcedureType.query.all()

    selected_procedure = request.args.get('procedure_type_id', type=int)

    query = ClinicIncome.query.join(Procedure).filter(
        ClinicIncome.clinic_id == current_user.clinic_id
    ).order_by(Procedure.procedure_date.desc())

    if selected_procedure:
        query = query.filter(Procedure.procedure_type_id == selected_procedure)

    clinic_income = query.all()

    # ✅ Calculate total clinic income sum
    total_clinic_income = sum(income.revenue for income in clinic_income)

    return render_template(
        'clinic_income/list.html',
        clinic_income=clinic_income,
        procedure_types=procedure_types,
        selected_procedure=selected_procedure,
        total_clinic_income=total_clinic_income
    )

from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.finance import OperatorEarnings
from . import operator_earnings_bp
from ...models import Operator, Procedure, ProcedureType


# 📌 Ensure Only Admins, Doctors, or Operators Can View Earnings
def earnings_access_control(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.role.role_name not in ["Admin", "Doctor", "Operator"]:
            flash("Access denied: You do not have permission to view earnings.", "danger")
            return redirect(url_for('dashboard'))
        return func(*args, **kwargs)
    return login_required(wrapper)

# 📌 List Operator Earnings (Admins & Doctors See All, Operators See Their Own)
@operator_earnings_bp.route('/', methods=['GET'])
@login_required
@earnings_access_control
def list_operator_earnings():
    operators = Operator.query.filter_by(clinic_id=current_user.clinic_id).all()
    procedure_types = ProcedureType.query.all()

    selected_operator = request.args.get('operator_id', type=int)
    selected_procedure = request.args.get('procedure_type_id', type=int)

    # ✅ Base query
    query = OperatorEarnings.query.join(Procedure).filter(
        OperatorEarnings.operator_id == Procedure.operator_id
    ).order_by(Procedure.procedure_date.desc())

    if current_user.role.role_name in ["Admin", "Doctor"]:
        # ✅ Admins & Doctors can filter by operator
        if selected_operator:
            query = query.filter(OperatorEarnings.operator_id == selected_operator)
    else:
        # ✅ Regular operators can ONLY see their own earnings
        user_operator = Operator.query.filter_by(
            clinic_id=current_user.clinic_id, phone=current_user.phone
        ).first()

        if not user_operator:
            flash("No earnings found for your account.", "warning")
            return redirect(url_for('dashboard'))

        query = query.filter(OperatorEarnings.operator_id == user_operator.operator_id)

    if selected_procedure:
        query = query.filter(Procedure.procedure_type_id == selected_procedure)

    earnings = query.all()

    # ✅ Calculate total earnings sum
    total_revenue = sum(e.revenue for e in earnings)
    total_operator_share = sum(e.operator_share for e in earnings)
    total_clinic_share = sum(e.clinic_share for e in earnings)

    return render_template(
        'operator_earnings/list.html',
        earnings=earnings,
        operators=operators,
        procedure_types=procedure_types,
        selected_operator=selected_operator,
        selected_procedure=selected_procedure,
        total_revenue=total_revenue,
        total_operator_share=total_operator_share,
        total_clinic_share=total_clinic_share
    )



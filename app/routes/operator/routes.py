from functools import wraps
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.operator import Operator, OperatorHistory
from app.models.clinic import Clinic
from . import operators_bp
from ...models import ProcedureType, Patient, Procedure, BodyRegion


# 📌 Ensure only Admins or Doctors can manage operators
def admin_or_doctor_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.role.role_name not in ["Admin", "Doctor"]:
            flash("Access denied: Only Admins and Doctors can manage operators.", "danger")
            return redirect(url_for('main.dashboard'))
        return func(*args, **kwargs)

    return login_required(wrapper)


# 📌 List All Operators (Admins see all, Doctors see only their clinic)
@operators_bp.route('/')
@login_required
@admin_or_doctor_required
def list_operators():
    if current_user.role.role_name == "Admin":
        operators = Operator.query.all()
    else:
        operators = Operator.query.filter_by(clinic_id=current_user.clinic_id).all()

    return render_template('operator/list.html', operators=operators)


# 📌 Add New Operator
@operators_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_or_doctor_required
def add_operator():
    clinics = Clinic.query.all() if current_user.role.role_name == "Admin" else [current_user.clinic]

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        specialty = request.form.get('specialty', None)
        experience_years = request.form.get('experience_years', None)
        clinic_id = request.form['clinic_id']

        new_operator = Operator(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            specialty=specialty,
            experience_years=experience_years,
            clinic_id=clinic_id
        )

        db.session.add(new_operator)
        db.session.commit()

        flash('Operator added successfully!', 'success')
        return redirect(url_for('operators.list_operators'))

    return render_template('operator/add.html', clinics=clinics)


# 📌 Edit Operator
@operators_bp.route('/<int:operator_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_or_doctor_required
def edit_operator(operator_id):
    operator = Operator.query.get_or_404(operator_id)

    # Ensure Doctors can only edit operators in their own clinic
    if current_user.role.role_name == "Doctor" and operator.clinic_id != current_user.clinic_id:
        flash("Access denied: You can only edit operators from your own clinic.", "danger")
        return redirect(url_for('operators.list_operators'))

    clinics = Clinic.query.all() if current_user.role.role_name == "Admin" else [current_user.clinic]

    if request.method == 'POST':
        operator.first_name = request.form['first_name']
        operator.last_name = request.form['last_name']
        operator.phone = request.form['phone']
        operator.specialty = request.form.get('specialty', None)
        operator.experience_years = request.form.get('experience_years', None)
        operator.clinic_id = request.form['clinic_id']

        db.session.commit()
        flash('Operator updated successfully!', 'success')
        return redirect(url_for('operators.list_operators'))

    return render_template('operator/edit.html', operator=operator, clinics=clinics)


# 📌 Delete Operator
@operators_bp.route('/<int:operator_id>/delete', methods=['POST'])
@login_required
@admin_or_doctor_required
def delete_operator(operator_id):
    operator = Operator.query.get_or_404(operator_id)

    # Ensure Doctors can only delete operators in their own clinic
    if current_user.role.role_name == "Doctor" and operator.clinic_id != current_user.clinic_id:
        flash("Access denied: You can only delete operators from your own clinic.", "danger")
        return redirect(url_for('operators.list_operators'))

    db.session.delete(operator)
    db.session.commit()
    flash('Operator deleted successfully!', 'success')
    return redirect(url_for('operators.list_operators'))

@operators_bp.route('/<int:operator_id>')
@login_required
@admin_or_doctor_required
def view_operator(operator_id):
    operator = Operator.query.get_or_404(operator_id)

    # Ensure Doctors can only view operators in their own clinic
    if current_user.role.role_name == "Doctor" and operator.clinic_id != current_user.clinic_id:
        flash("Access denied: You can only view operators from your own clinic.", "danger")
        return redirect(url_for('operators.list_operators'))

    # Fetch all procedures performed by this operator with details
    history = (
        db.session.query(
            OperatorHistory.history_id,
            Procedure.procedure_date,
            Patient.patient_id,  # ✅ Explicitly select patient_id
            Patient.first_name.label("patient_first_name"),
            Patient.last_name.label("patient_last_name"),
            ProcedureType.name.label("procedure_type"),
            BodyRegion.name.label("body_region")
        )
        .join(Procedure, OperatorHistory.procedure_id == Procedure.procedure_id)
        .join(Patient, OperatorHistory.patient_id == Patient.patient_id)
        .join(ProcedureType, Procedure.procedure_type_id == ProcedureType.procedure_type_id)
        .join(BodyRegion, Procedure.body_region_id == BodyRegion.body_region_id)
        .filter(OperatorHistory.operator_id == operator_id)
        .all()
    )

    return render_template('operator/details.html', operator=operator, history=history)

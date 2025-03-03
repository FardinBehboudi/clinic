from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.patient import Patient, PatientHistory
from . import patients_bp
from ...models import Procedure, ProcedureType, Operator, BodyRegion


# 📌 List All Patients
@patients_bp.route('/')
@login_required
def list_patients():
    patients = Patient.query.filter_by(clinic_id=current_user.clinic_id).all()
    return render_template('patient/list.html', patients=patients)

# 📌 Add New Patient
@patients_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_patient():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        email = request.form.get('email', None)
        date_of_birth = request.form.get('date_of_birth', None)
        medical_history = request.form.get('medical_history', None)

        # ✅ Check if a patient with the same phone exists in the same clinic
        existing_patient = Patient.query.filter_by(clinic_id=current_user.clinic_id, phone=phone).first()
        if existing_patient:
            flash("Error: A patient with this phone number already exists in your clinic.", "danger")
            return redirect(url_for('patients.add_patient'))

        new_patient = Patient(
            clinic_id=current_user.clinic_id,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            email=email,
            date_of_birth=date_of_birth,
            medical_history=medical_history
        )

        try:
            db.session.add(new_patient)
            db.session.commit()
            flash('Patient added successfully!', 'success')
            return redirect(url_for('patients.list_patients'))
        except IntegrityError:
            db.session.rollback()  # Rollback transaction to prevent corruption
            flash("Error: A patient with this phone number already exists in your clinic.", "danger")
            return redirect(url_for('patients.add_patient'))

    return render_template('patient/add.html')


# 📌 View Patient Details
@patients_bp.route('/<int:patient_id>')
@login_required
def view_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    # Fetch all procedures related to this patient with details
    history = (
        db.session.query(
            PatientHistory.history_id,
            Procedure.procedure_date,
            Procedure.price,
            Operator.first_name.label("operator_first_name"),
            Operator.last_name.label("operator_last_name"),
            ProcedureType.name.label("procedure_type"),
            BodyRegion.name.label("body_region"),
            Procedure.brand
        )
        .join(Procedure, PatientHistory.procedure_id == Procedure.procedure_id)
        .join(Operator, PatientHistory.operator_id == Operator.operator_id)
        .join(ProcedureType, Procedure.procedure_type_id == ProcedureType.procedure_type_id)
        .join(BodyRegion, Procedure.body_region_id == BodyRegion.body_region_id)
        .filter(PatientHistory.patient_id == patient_id)
        .all()
    )

    return render_template('patient/details.html', patient=patient, history=history)

# 📌 Edit Patient
@patients_bp.route('/<int:patient_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    if request.method == 'POST':
        patient.first_name = request.form['first_name']
        patient.last_name = request.form['last_name']
        patient.phone = request.form['phone']
        patient.email = request.form.get('email', None)
        patient.date_of_birth = request.form['date_of_birth']
        patient.medical_history = request.form['medical_history']

        db.session.commit()
        flash('Patient updated successfully!', 'success')
        return redirect(url_for('patients.list_patients'))

    return render_template('patient/edit.html', patient=patient)

# 📌 Delete Patient
@patients_bp.route('/<int:patient_id>/delete', methods=['POST'])
@login_required
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    flash('Patient deleted successfully!', 'success')
    return redirect(url_for('patients.list_patients'))

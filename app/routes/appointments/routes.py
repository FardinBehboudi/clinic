from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app.extensions import db
from app.models.appointment import Appointment, AppointmentStatus
from app.models.patient import Patient
from app.models.operator import Operator
from app.models.procedure import ProcedureType
from . import appointments_bp


# 📌 List All Appointments (Sorted by Date, Upcoming First)
@appointments_bp.route('/', methods=['GET'])
@login_required
def list_appointments():
    operators = Operator.query.filter_by(clinic_id=current_user.clinic_id).all()
    patients = Patient.query.filter_by(clinic_id=current_user.clinic_id).all()
    procedure_types = ProcedureType.query.all()

    # ✅ Get filter values from request
    selected_operator = request.args.get('operator_id', type=int)
    selected_patient = request.args.get('patient_id', type=int)
    selected_procedure = request.args.get('procedure_type_id', type=int)
    selected_date = request.args.get('appointment_date')

    # ✅ Base query (Sort by nearest upcoming appointment first)
    query = Appointment.query.filter_by(clinic_id=current_user.clinic_id).order_by(Appointment.appointment_date.asc())

    # ✅ Apply filters if selected
    if selected_operator:
        query = query.filter(Appointment.operator_id == selected_operator)
    if selected_patient:
        query = query.filter(Appointment.patient_id == selected_patient)
    if selected_procedure:
        query = query.filter(Appointment.procedure_type_id == selected_procedure)
    if selected_date:
        query = query.filter(Appointment.appointment_date == selected_date)

    appointments = query.all()

    return render_template(
        'appointments/list.html',
        appointments=appointments,
        operators=operators,
        patients=patients,
        procedure_types=procedure_types,
        selected_operator=selected_operator,
        selected_patient=selected_patient,
        selected_procedure=selected_procedure,
        selected_date=selected_date
    )



# 📌 Add a New Appointment
@appointments_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_appointment():
    patients = Patient.query.filter_by(clinic_id=current_user.clinic_id).all()
    operators = Operator.query.filter_by(clinic_id=current_user.clinic_id).all()
    procedure_types = ProcedureType.query.all()
    statuses = AppointmentStatus.query.all()

    if request.method == 'POST':
        patient_id = request.form['patient_id']
        operator_id = request.form['operator_id']
        procedure_type_id = request.form['procedure_type_id']
        appointment_date = datetime.strptime(request.form['appointment_date'], "%Y-%m-%d")
        appointment_title = request.form['appointment_title']
        status_id = request.form['status_id']
        note = request.form.get('note', None)

        new_appointment = Appointment(
            clinic_id=current_user.clinic_id,
            patient_id=patient_id,
            operator_id=operator_id,
            procedure_type_id=procedure_type_id,
            appointment_date=appointment_date,
            appointment_title=appointment_title,
            status_id=status_id,
            note=note
        )

        db.session.add(new_appointment)
        db.session.commit()

        flash('Appointment added successfully!', 'success')
        return redirect(url_for('appointments.list_appointments'))

    return render_template(
        'appointments/add.html',
        patients=patients,
        operators=operators,
        procedure_types=procedure_types,
        statuses=statuses
    )


# 📌 View Appointment Details
@appointments_bp.route('/<int:appointment_id>')
@login_required
def view_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)

    return render_template('appointments/details.html', appointment=appointment)

@appointments_bp.route('/<int:appointment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)

    # Ensure only users from the same clinic can edit
    if appointment.clinic_id != current_user.clinic_id:
        flash("Access denied: You can only edit appointments from your clinic.", "danger")
        return redirect(url_for('appointments.list_appointments'))

    patients = Patient.query.filter_by(clinic_id=current_user.clinic_id).all()
    operators = Operator.query.filter_by(clinic_id=current_user.clinic_id).all()
    procedure_types = ProcedureType.query.all()
    statuses = AppointmentStatus.query.all()

    if request.method == 'POST':
        appointment.patient_id = request.form['patient_id']
        appointment.operator_id = request.form['operator_id']
        appointment.procedure_type_id = request.form['procedure_type_id']
        appointment.appointment_date = request.form['appointment_date']
        appointment.appointment_title = request.form['appointment_title']
        appointment.status_id = request.form['status_id']
        appointment.note = request.form.get('note', None)

        db.session.commit()
        flash("Appointment updated successfully!", "success")
        return redirect(url_for('appointments.list_appointments'))

    return render_template(
        'appointments/edit.html',
        appointment=appointment,
        patients=patients,
        operators=operators,
        procedure_types=procedure_types,
        statuses=statuses
    )

@appointments_bp.route('/<int:appointment_id>/delete', methods=['POST'])
@login_required
def delete_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)

    # ✅ Only Admins & Doctors can delete appointments
    if current_user.role.role_name not in ["Admin", "Doctor"]:
        flash("Access denied: Only Admins and Doctors can delete appointments.", "danger")
        return redirect(url_for('appointments.list_appointments'))

    db.session.delete(appointment)
    db.session.commit()
    flash("Appointment deleted successfully!", "success")
    return redirect(url_for('appointments.list_appointments'))

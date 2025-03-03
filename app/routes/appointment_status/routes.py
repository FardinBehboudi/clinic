from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.appointment import AppointmentStatus
from . import appointment_status_bp


# 📌 Ensure Only Admins & Doctors Can Manage Statuses
def admin_or_doctor_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.role.role_name not in ["Admin", "Doctor"]:
            flash("Access denied: Only Admins and Doctors can manage appointment statuses.", "danger")
            return redirect(url_for('dashboard'))
        return func(*args, **kwargs)
    return login_required(wrapper)


# 📌 List All Appointment Statuses
@appointment_status_bp.route('/')
@login_required
@admin_or_doctor_required
def list_statuses():
    statuses = AppointmentStatus.query.all()
    return render_template('appointment_status/list.html', statuses=statuses)


# 📌 Add a New Appointment Status
@appointment_status_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_or_doctor_required
def add_status():
    if request.method == 'POST':
        status_name = request.form['status_name']

        if AppointmentStatus.query.filter_by(status_name=status_name).first():
            flash("Status already exists!", "danger")
            return redirect(url_for('appointment_status.list_statuses'))

        new_status = AppointmentStatus(status_name=status_name)
        db.session.add(new_status)
        db.session.commit()

        flash("Appointment status added successfully!", "success")
        return redirect(url_for('appointment_status.list_statuses'))

    return render_template('appointment_status/add.html')


# 📌 Edit an Appointment Status
@appointment_status_bp.route('/<int:status_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_or_doctor_required
def edit_status(status_id):
    status = AppointmentStatus.query.get_or_404(status_id)

    if request.method == 'POST':
        status.status_name = request.form['status_name']
        db.session.commit()
        flash("Appointment status updated successfully!", "success")
        return redirect(url_for('appointment_status.list_statuses'))

    return render_template('appointment_status/edit.html', status=status)


# 📌 Delete an Appointment Status
@appointment_status_bp.route('/<int:status_id>/delete', methods=['POST'])
@login_required
@admin_or_doctor_required
def delete_status(status_id):
    status = AppointmentStatus.query.get_or_404(status_id)
    db.session.delete(status)
    db.session.commit()
    flash("Appointment status deleted successfully!", "success")
    return redirect(url_for('appointment_status.list_statuses'))

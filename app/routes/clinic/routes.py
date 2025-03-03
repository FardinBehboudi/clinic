from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.clinic import Clinic
from . import clinics_bp

# 📌 List All Clinics
@clinics_bp.route('/')
@login_required
def list_clinics():
    clinics = Clinic.query.all()
    return render_template('clinic/list.html', clinics=clinics)

# 📌 Add New Clinic
@clinics_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_clinic():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        email = request.form.get('email', None)
        website = request.form.get('website', None)

        # Create new clinic
        new_clinic = Clinic(
            name=name,
            address=address,
            phone=phone,
            email=email,
            website=website
        )
        db.session.add(new_clinic)
        db.session.commit()

        # Assign the new clinic_id to the logged-in admin
        current_user.clinic_id = new_clinic.clinic_id
        db.session.commit()

        flash('Clinic created successfully! You are now assigned to this clinic.', 'success')
        return redirect(url_for('clinics.list_clinics'))

    return render_template('clinic/add.html')


# 📌 View Clinic Details
@clinics_bp.route('/<int:clinic_id>')
@login_required
def view_clinic(clinic_id):
    clinic = Clinic.query.get_or_404(clinic_id)
    return render_template('clinic/details.html', clinic=clinic)

# 📌 Edit Clinic
@clinics_bp.route('/<int:clinic_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_clinic(clinic_id):
    clinic = Clinic.query.get_or_404(clinic_id)

    if request.method == 'POST':
        clinic.name = request.form['name']
        clinic.address = request.form['address']
        clinic.phone = request.form['phone']
        clinic.email = request.form.get('email', None)
        clinic.website = request.form.get('website', None)

        db.session.commit()
        flash('Clinic updated successfully!', 'success')
        return redirect(url_for('clinics.list_clinics'))

    return render_template('clinic/edit.html', clinic=clinic)

# 📌 Delete Clinic
@clinics_bp.route('/<int:clinic_id>/delete', methods=['POST'])
@login_required
def delete_clinic(clinic_id):
    clinic = Clinic.query.get_or_404(clinic_id)
    db.session.delete(clinic)
    db.session.commit()
    flash('Clinic deleted successfully!', 'success')
    return redirect(url_for('clinics.list_clinics'))

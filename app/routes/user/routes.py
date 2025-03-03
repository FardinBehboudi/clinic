from functools import wraps

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models.user import User, Role
from app.models.clinic import Clinic
from . import users_bp

def admin_or_doctor_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.role.role_name == "Admin":
            return func(*args, **kwargs)
        elif current_user.role.role_name == "Doctor":
            return func(*args, **kwargs)
        else:
            flash("Access denied: Only Admins and Doctors can manage users.", "danger")
            return redirect(url_for('main.dashboard'))
    return login_required(wrapper)

# 📌 List All Users
@users_bp.route('/')
@login_required
@admin_or_doctor_required
def list_users():
    if current_user.role.role_name == "Admin":
        users = User.query.all()  # Admin sees all users
    else:
        users = User.query.filter_by(clinic_id=current_user.clinic_id).all()  # Doctor sees only their clinic's users

    return render_template('user/list.html', users=users)


# 📌 Add New User
@users_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_or_doctor_required
def add_user():
    clinics = Clinic.query.all() if current_user.role.role_name == "Admin" else [current_user.clinic]

    # ✅ Allow Doctors to assign the Doctor role, but only within their clinic
    if current_user.role.role_name == "Doctor":
        roles = Role.query.filter(Role.role_name.notin_(["Admin"])).all()
    else:
        roles = Role.query.all()

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        clinic_id = request.form['clinic_id']
        role_id = request.form['role_id']

        # ✅ Ensure Doctor users cannot create Admin accounts
        if current_user.role.role_name == "Doctor":
            selected_role = Role.query.get(role_id)
            if selected_role.role_name == "Admin":
                flash("Access denied: Doctors cannot create Admin users.", "danger")
                return redirect(url_for('users.add_user'))

        # Ensure user does not already exist
        if User.query.filter_by(email=email).first():
            flash("Email is already registered.", "danger")
            return redirect(url_for('users.add_user'))

        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            clinic_id=clinic_id,
            role_id=role_id
        )
        new_user.password_hash = generate_password_hash(password)  # Set default password

        db.session.add(new_user)
        db.session.commit()

        flash('User created successfully!', 'success')
        return redirect(url_for('users.list_users'))

    return render_template('user/add.html', clinics=clinics, roles=roles)



# 📌 Edit User
@users_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_or_doctor_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    # Ensure Doctor users can only edit users in their clinic
    if current_user.role.role_name == "Doctor" and user.clinic_id != current_user.clinic_id:
        flash("Access denied: You can only edit users from your own clinic.", "danger")
        return redirect(url_for('users.list_users'))

    clinics = Clinic.query.all() if current_user.role.role_name == "Admin" else [current_user.clinic]

    # ✅ Allow Doctors to reassign the Doctor role, but not Admin
    if current_user.role.role_name == "Doctor":
        roles = Role.query.filter(Role.role_name.notin_(["Admin"])).all()
    else:
        roles = Role.query.all()

    if request.method == 'POST':
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.phone = request.form['phone']
        user.email = request.form['email']
        user.clinic_id = request.form['clinic_id']
        user.role_id = request.form['role_id']

        # ✅ Prevent Doctor from assigning Admin role
        if current_user.role.role_name == "Doctor":
            selected_role = Role.query.get(user.role_id)
            if selected_role.role_name == "Admin":
                flash("Access denied: Doctors cannot assign Admin roles.", "danger")
                return redirect(url_for('users.list_users'))

        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('users.list_users'))

    return render_template('user/edit.html', user=user, clinics=clinics, roles=roles)


# 📌 Delete User
@users_bp.route('/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_or_doctor_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    # Ensure Doctor users can only delete users from their clinic
    if current_user.role.role_name == "Doctor" and user.clinic_id != current_user.clinic_id:
        flash("Access denied: You can only delete users from your own clinic.", "danger")
        return redirect(url_for('users.list_users'))

    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('users.list_users'))

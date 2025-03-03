from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import Role
from . import roles_bp
from functools import wraps

# 📌 Ensure only admins can access this section
def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.role.role_name != "Admin":
            flash("Access denied: Admins only.", "danger")
            return redirect(url_for('main.dashboard'))
        return func(*args, **kwargs)
    return login_required(wrapper)

# 📌 List All Roles
@roles_bp.route('/')
@admin_required
def list_roles():
    roles = Role.query.all()
    return render_template('role/list.html', roles=roles)

# 📌 Add New Role
@roles_bp.route('/add', methods=['GET', 'POST'])
@admin_required
def add_role():
    if request.method == 'POST':
        role_name = request.form['role_name']

        # Ensure role does not already exist
        if Role.query.filter_by(role_name=role_name).first():
            flash("Role already exists.", "danger")
            return redirect(url_for('roles.add_role'))

        new_role = Role(role_name=role_name)
        db.session.add(new_role)
        db.session.commit()

        flash('Role added successfully!', 'success')
        return redirect(url_for('roles.list_roles'))

    return render_template('role/add.html')

# 📌 Edit Role
@roles_bp.route('/<int:role_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_role(role_id):
    role = Role.query.get_or_404(role_id)

    if request.method == 'POST':
        role.role_name = request.form['role_name']
        db.session.commit()
        flash('Role updated successfully!', 'success')
        return redirect(url_for('roles.list_roles'))

    return render_template('role/edit.html', role=role)

# 📌 Delete Role
@roles_bp.route('/<int:role_id>/delete', methods=['POST'])
@admin_required
def delete_role(role_id):
    role = Role.query.get_or_404(role_id)

    # Ensure we do not delete predefined roles
    if role.role_name in ["Admin", "Doctor", "Operator", "Secretary"]:
        flash("Cannot delete predefined system roles.", "danger")
        return redirect(url_for('roles.list_roles'))

    db.session.delete(role)
    db.session.commit()
    flash('Role deleted successfully!', 'success')
    return redirect(url_for('roles.list_roles'))

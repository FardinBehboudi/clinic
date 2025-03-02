from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models.user import User
from flask import Blueprint

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')


@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.first_name = request.form['first_name']
        current_user.last_name = request.form['last_name']
        current_user.phone = request.form['phone']

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('profile.edit_profile'))

    return render_template('auth/edit_profile.html')


@profile_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']

        if not current_user.check_password(old_password):
            flash("Old password is incorrect.", "danger")
            return redirect(url_for('profile.change_password'))

        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()

        flash("Password updated successfully!", "success")
        return redirect(url_for('profile.edit_profile'))

    return render_template('auth/change_password.html')

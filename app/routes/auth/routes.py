from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from app.extensions import db, login_manager
from app.models.user import User , Role
from . import auth_bp

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))  # ✅ Corrected URL
        else:
            flash('Invalid credentials', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # If an admin already exists, disable registration
    if User.query.count() > 0:
        flash("Registration is disabled. Only Admins and Doctors can add users.", "danger")
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('auth.register'))

        # The first user is always an Admin
        role = Role.query.filter_by(role_name="Admin").first()
        if not role:
            flash("Error: No 'Admin' role found. Please create roles first.", "danger")
            return redirect(url_for('auth.register'))

        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            role_id=role.role_id,  # Assign Admin role
            is_first_admin=True
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('First Admin created successfully! You can log in now.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


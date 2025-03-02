from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from . import main_bp

@main_bp.route('/')
def home():
    """Redirect root URL to the dashboard"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))  # Redirect to login if not logged in

@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

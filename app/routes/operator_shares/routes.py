from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.finance import OperatorShare
from app.models.operator import Operator
from . import operator_shares_bp

# 📌 Ensure only Admins or Doctors can modify operator shares
def admin_or_doctor_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.role.role_name not in ["Admin", "Doctor"]:
            flash("Access denied: Only Admins or Doctors can manage operator shares.", "danger")
            return redirect(url_for('operator_shares.list_operator_shares'))
        return func(*args, **kwargs)
    return login_required(wrapper)

# 📌 List All Operator Shares (Only for Admins & Doctors)
@operator_shares_bp.route('/')
@login_required
@admin_or_doctor_required
def list_operator_shares():
    operator_shares = OperatorShare.query.join(Operator).filter(Operator.clinic_id == current_user.clinic_id).all()
    return render_template('operator_shares/list.html', operator_shares=operator_shares)

# 📌 Add a New Operator Share
@operator_shares_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_or_doctor_required
def add_operator_share():
    operators = Operator.query.filter_by(clinic_id=current_user.clinic_id).all()

    if request.method == 'POST':
        operator_id = request.form['operator_id']
        clinic_percentage = request.form['clinic_percentage']
        operator_percentage = request.form['operator_percentage']

        new_share = OperatorShare(
            operator_id=operator_id,
            clinic_percentage=clinic_percentage,
            operator_percentage=operator_percentage
        )

        db.session.add(new_share)
        db.session.commit()
        flash('Operator share added successfully!', 'success')
        return redirect(url_for('operator_shares.list_operator_shares'))

    return render_template('operator_shares/add.html', operators=operators)

# 📌 Edit an Operator Share
@operator_shares_bp.route('/<int:share_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_or_doctor_required
def edit_operator_share(share_id):
    share = OperatorShare.query.get_or_404(share_id)

    # Ensure the operator belongs to the same clinic
    if share.operator.clinic_id != current_user.clinic_id:
        flash("Access denied: You can only edit shares for operators in your clinic.", "danger")
        return redirect(url_for('operator_shares.list_operator_shares'))

    if request.method == 'POST':
        share.clinic_percentage = request.form['clinic_percentage']
        share.operator_percentage = request.form['operator_percentage']

        db.session.commit()
        flash('Operator share updated successfully!', 'success')
        return redirect(url_for('operator_shares.list_operator_shares'))

    return render_template('operator_shares/edit.html', share=share)

# 📌 Delete an Operator Share
@operator_shares_bp.route('/<int:share_id>/delete', methods=['POST'])
@login_required
@admin_or_doctor_required
def delete_operator_share(share_id):
    share = OperatorShare.query.get_or_404(share_id)

    # Ensure the operator belongs to the same clinic
    if share.operator.clinic_id != current_user.clinic_id:
        flash("Access denied: You can only delete shares for operators in your clinic.", "danger")
        return redirect(url_for('operator_shares.list_operator_shares'))

    db.session.delete(share)
    db.session.commit()
    flash('Operator share deleted successfully!', 'success')
    return redirect(url_for('operator_shares.list_operator_shares'))

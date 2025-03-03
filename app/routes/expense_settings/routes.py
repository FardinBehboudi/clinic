from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.expense import ExpenseType, ExpenseCategory
from . import expense_settings_bp


# 📌 Ensure Only Admins & Doctors Can Manage Expense Settings
def admin_or_doctor_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.role.role_name not in ["Admin", "Doctor"]:
            flash("Access denied: Only Admins and Doctors can manage expense settings.", "danger")
            return redirect(url_for('dashboard'))
        return func(*args, **kwargs)
    return login_required(wrapper)


# 📌 List All Expense Types & Categories
@expense_settings_bp.route('/')
@login_required
@admin_or_doctor_required
def list_expense_settings():
    expense_types = ExpenseType.query.all()
    expense_categories = ExpenseCategory.query.all()
    return render_template('expense_settings/list.html', expense_types=expense_types, expense_categories=expense_categories)


# 📌 Add a New Expense Type
@expense_settings_bp.route('/type/add', methods=['GET', 'POST'])
@login_required
@admin_or_doctor_required
def add_expense_type():
    if request.method == 'POST':
        type_name = request.form['type_name']

        if ExpenseType.query.filter_by(type_name=type_name).first():
            flash("Expense type already exists!", "danger")
            return redirect(url_for('expense_settings.list_expense_settings'))

        new_type = ExpenseType(type_name=type_name)
        db.session.add(new_type)
        db.session.commit()

        flash("Expense type added successfully!", "success")
        return redirect(url_for('expense_settings.list_expense_settings'))

    return render_template('expense_settings/add_type.html')


# 📌 Add a New Expense Category
@expense_settings_bp.route('/category/add', methods=['GET', 'POST'])
@login_required
@admin_or_doctor_required
def add_expense_category():
    expense_types = ExpenseType.query.all()

    if request.method == 'POST':
        expense_type_id = request.form['expense_type_id']
        category_name = request.form['category_name']

        if ExpenseCategory.query.filter_by(category_name=category_name, expense_type_id=expense_type_id).first():
            flash("Expense category already exists for this type!", "danger")
            return redirect(url_for('expense_settings.list_expense_settings'))

        new_category = ExpenseCategory(expense_type_id=expense_type_id, category_name=category_name)
        db.session.add(new_category)
        db.session.commit()

        flash("Expense category added successfully!", "success")
        return redirect(url_for('expense_settings.list_expense_settings'))

    return render_template('expense_settings/add_category.html', expense_types=expense_types)


# 📌 Edit an Expense Type
@expense_settings_bp.route('/type/<int:type_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_or_doctor_required
def edit_expense_type(type_id):
    expense_type = ExpenseType.query.get_or_404(type_id)

    if request.method == 'POST':
        expense_type.type_name = request.form['type_name']
        db.session.commit()
        flash("Expense type updated successfully!", "success")
        return redirect(url_for('expense_settings.list_expense_settings'))

    return render_template('expense_settings/edit_type.html', expense_type=expense_type)


# 📌 Edit an Expense Category
@expense_settings_bp.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_or_doctor_required
def edit_expense_category(category_id):
    expense_category = ExpenseCategory.query.get_or_404(category_id)
    expense_types = ExpenseType.query.all()

    if request.method == 'POST':
        expense_category.expense_type_id = request.form['expense_type_id']
        expense_category.category_name = request.form['category_name']
        db.session.commit()
        flash("Expense category updated successfully!", "success")
        return redirect(url_for('expense_settings.list_expense_settings'))

    return render_template('expense_settings/edit_category.html', expense_category=expense_category, expense_types=expense_types)


# 📌 Delete an Expense Type
@expense_settings_bp.route('/type/<int:type_id>/delete', methods=['POST'])
@login_required
@admin_or_doctor_required
def delete_expense_type(type_id):
    expense_type = ExpenseType.query.get_or_404(type_id)
    db.session.delete(expense_type)
    db.session.commit()
    flash("Expense type deleted successfully!", "success")
    return redirect(url_for('expense_settings.list_expense_settings'))


# 📌 Delete an Expense Category
@expense_settings_bp.route('/category/<int:category_id>/delete', methods=['POST'])
@login_required
@admin_or_doctor_required
def delete_expense_category(category_id):
    expense_category = ExpenseCategory.query.get_or_404(category_id)
    db.session.delete(expense_category)
    db.session.commit()
    flash("Expense category deleted successfully!", "success")
    return redirect(url_for('expense_settings.list_expense_settings'))

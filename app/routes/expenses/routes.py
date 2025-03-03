from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app.extensions import db
from app.models.expense import Expenses, ExpenseType, ExpenseCategory, Inventory
from . import expenses_bp

def admin_or_doctor_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.role.role_name not in ["Admin", "Doctor"]:
            flash("Access denied: Only Admins and Doctors can add expenses.", "danger")
            return redirect(url_for('expenses.list_expenses'))
        return func(*args, **kwargs)
    return login_required(wrapper)

# 📌 add new Expenses
@expenses_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_or_doctor_required
def add_expense():
    expense_types = ExpenseType.query.all()
    expense_categories = ExpenseCategory.query.all()

    if request.method == 'POST':
        expense_type_id = request.form['expense_type_id']
        expense_category_id = request.form['expense_category_id']
        brand = request.form.get('brand', None)
        quantity = request.form.get('quantity', None)  # Can be NULL
        unit = request.form.get('unit', None)
        total_price = float(request.form['total_price'])
        purchase_date = request.form['purchase_date']
        provider = request.form.get('provider', None)
        is_stock = request.form.get('is_stock', False)  # ✅ Checkbox to mark as stock item

        new_expense = Expenses(
            clinic_id=current_user.clinic_id,
            expense_type_id=expense_type_id,
            expense_category_id=expense_category_id,
            brand=brand,
            quantity=quantity,
            unit=unit,
            total_price=total_price,
            purchase_date=purchase_date,
            provider=provider
        )

        db.session.add(new_expense)
        db.session.commit()

        # ✅ Fetch the selected expense category from the database
        expense_category = ExpenseCategory.query.get(expense_category_id)

        # ✅ Add to Inventory if it's a stock item
        if is_stock and quantity and float(quantity) > 0:
            price_per_unit = total_price / float(quantity)
            new_inventory = Inventory(
                expense_id=new_expense.expense_id,
                category_name=expense_category.category_name if expense_category else "Unknown",
                brand=brand,
                price_per_unit=price_per_unit,
                quantity_available=float(quantity)
            )
            db.session.add(new_inventory)
            db.session.commit()

        flash('Expense added successfully!', 'success')
        return redirect(url_for('expenses.list_expenses'))

    return render_template('expenses/add.html', expense_types=expense_types, expense_categories=expense_categories)

# 📌 List All Expenses (Sorted by Date, Latest First)
@expenses_bp.route('/', methods=['GET'])
@login_required
@admin_or_doctor_required
def list_expenses():
    expense_types = ExpenseType.query.all()
    expense_categories = ExpenseCategory.query.all()

    selected_type = request.args.get('expense_type_id', type=int)
    selected_category = request.args.get('expense_category_id', type=int)
    selected_date = request.args.get('purchase_date')

    query = Expenses.query.filter_by(clinic_id=current_user.clinic_id).order_by(Expenses.purchase_date.desc())

    if selected_type:
        query = query.filter(Expenses.expense_type_id == selected_type)
    if selected_category:
        query = query.filter(Expenses.expense_category_id == selected_category)
    if selected_date:
        query = query.filter(Expenses.purchase_date == selected_date)

    expenses = query.all()

    # ✅ Calculate total expense sum
    total_expense = sum(expense.total_price for expense in expenses)

    return render_template(
        'expenses/list.html',
        expenses=expenses,
        expense_types=expense_types,
        expense_categories=expense_categories,
        selected_type=selected_type,
        selected_category=selected_category,
        selected_date=selected_date,
        total_expense=total_expense
    )

# 📌 Edit an Expense
@expenses_bp.route('/<int:expense_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_or_doctor_required
def edit_expense(expense_id):
    expense = Expenses.query.get_or_404(expense_id)

    if expense.clinic_id != current_user.clinic_id:
        flash("Access denied: You can only edit expenses from your clinic.", "danger")
        return redirect(url_for('expenses.list_expenses'))

    expense_types = ExpenseType.query.all()
    expense_categories = ExpenseCategory.query.all()

    if request.method == 'POST':
        expense.expense_type_id = request.form['expense_type_id']
        expense.expense_category_id = request.form['expense_category_id']
        expense.brand = request.form.get('brand', None)
        expense.quantity = request.form['quantity']
        expense.unit = request.form.get('unit', None)
        expense.total_price = request.form['total_price']
        expense.purchase_date = request.form['purchase_date']
        expense.provider = request.form.get('provider', None)

        db.session.commit()
        flash("Expense updated successfully!", "success")
        return redirect(url_for('expenses.list_expenses'))

    return render_template('expenses/edit.html', expense=expense, expense_types=expense_types, expense_categories=expense_categories)


# 📌 Delete an Expense
@expenses_bp.route('/<int:expense_id>/delete', methods=['POST'])
@login_required
@admin_or_doctor_required
def delete_expense(expense_id):
    expense = Expenses.query.get_or_404(expense_id)

    if expense.clinic_id != current_user.clinic_id:
        flash("Access denied: You can only delete expenses from your clinic.", "danger")
        return redirect(url_for('expenses.list_expenses'))

    # ✅ Remove associated inventory entry if exists
    inventory_item = Inventory.query.filter_by(expense_id=expense.expense_id).first()
    if inventory_item:
        db.session.delete(inventory_item)

    db.session.delete(expense)
    db.session.commit()
    flash("Expense and associated inventory deleted successfully!", "success")
    return redirect(url_for('expenses.list_expenses'))


@expenses_bp.route('/<int:expense_id>')
@login_required
@admin_or_doctor_required
def view_expense(expense_id):
    expense = Expenses.query.get_or_404(expense_id)

    return render_template('expenses/details.html', expense=expense)

@expenses_bp.route('/get-categories/<int:expense_type_id>')
@login_required
def get_categories(expense_type_id):
    categories = ExpenseCategory.query.filter_by(expense_type_id=expense_type_id).all()
    category_list = [{"id": category.expense_category_id, "name": category.category_name} for category in categories]
    return jsonify(category_list)

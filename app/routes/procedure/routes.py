from functools import wraps
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.procedure import Procedure, ProcedureType, BodyRegion, ProcedureTypeBodyRegion
from app.models.patient import Patient, PatientHistory
from app.models.operator import Operator, OperatorHistory
from . import procedures_bp
from ...models import OperatorEarnings, ClinicIncome, OperatorShare, Expenses, Inventory, ProcedureMaterialCost


# 📌 Ensure only Admins or Doctors can edit/delete any procedure
def admin_or_doctor_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.role.role_name in ["Admin", "Doctor"]:
            return func(*args, **kwargs)
        else:
            flash("Access denied: Only Admins or Doctors can modify procedures.", "danger")
            return redirect(url_for('procedures.list_procedures'))
    return login_required(wrapper)

# 📌 List All Procedures (Filtered by Clinic)
@procedures_bp.route('/')
@login_required
def list_procedures():
    procedures = Procedure.query.options(
        db.joinedload(Procedure.procedure_material_costs).joinedload(ProcedureMaterialCost.inventory)
    ).filter_by(clinic_id=current_user.clinic_id).all()

    # Find the logged-in user's corresponding Operator record (if exists)
    user_operator = Operator.query.filter_by(clinic_id=current_user.clinic_id, phone=current_user.phone).first()
    user_operator_id = user_operator.operator_id if user_operator else None  # Get the operator_id if found

    return render_template('procedure/list.html', procedures=procedures, user_operator_id=user_operator_id)

# 📌 Add a New Procedure
@procedures_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_procedure():
    # Find the matching operator based on clinic_id and phone number
    logged_in_operator = Operator.query.filter_by(
        clinic_id=current_user.clinic_id, phone=current_user.phone
    ).first()

    patients = Patient.query.filter_by(clinic_id=current_user.clinic_id).all()
    operators = Operator.query.filter_by(clinic_id=current_user.clinic_id).all()
    procedure_types = ProcedureType.query.all()
    body_regions = BodyRegion.query.all()
    categories = db.session.query(Inventory.category_name).distinct().all()  # ✅ Fetch unique categories

    if request.method == 'POST':
        patient_id = request.form['patient_id']
        operator_id = request.form['operator_id']
        procedure_type_id = request.form['procedure_type_id']
        body_region_id = request.form['body_region_id']
        procedure_date = request.form['procedure_date']
        price = request.form['price']

        new_procedure = Procedure(
            clinic_id=current_user.clinic_id,
            patient_id=patient_id,
            operator_id=operator_id,
            procedure_type_id=procedure_type_id,
            body_region_id=body_region_id,
            procedure_date=procedure_date,
            price=price
        )

        db.session.add(new_procedure)
        db.session.commit()

        # ✅ Add Procedure Materials (if any)
        inventory_ids = request.form.getlist('inventory_id')
        material_quantities = request.form.getlist('material_quantity')

        for i in range(len(inventory_ids)):
            if inventory_ids[i] and material_quantities[i]:
                inventory_item = Inventory.query.get(inventory_ids[i])
                quantity_used = float(material_quantities[i])

                if inventory_item.update_stock(quantity_used):  # ✅ Check stock availability
                    procedure_material_cost = ProcedureMaterialCost(
                        procedure_id=new_procedure.procedure_id,
                        inventory_id=inventory_item.inventory_id,
                        quantity_used=quantity_used,
                        unit=inventory_item.expense.unit
                    )
                    db.session.add(procedure_material_cost)
                else:
                    flash(f"Not enough stock for {inventory_item.brand} ({inventory_item.category_name}).", "danger")

        db.session.commit()
        flash('Procedure added successfully!', 'success')
        return redirect(url_for('procedures.list_procedures'))

    return render_template(
        'procedure/add.html',
        patients=patients,
        operators=operators,
        procedure_types=procedure_types,
        body_regions=body_regions,
        categories=[c[0] for c in categories],  # ✅ Send categories to template
        logged_in_operator=logged_in_operator
    )


@procedures_bp.route('/<int:procedure_id>')
@login_required
def view_procedure(procedure_id):
    procedure = Procedure.query.options(
        db.joinedload(Procedure.procedure_material_costs).joinedload(ProcedureMaterialCost.inventory)
    ).get_or_404(procedure_id)

    if procedure.clinic_id != current_user.clinic_id:
        flash("Access denied: You can only view procedures from your clinic.", "danger")
        return redirect(url_for('procedures.list_procedures'))

    return render_template('procedure/details.html', procedure=procedure)

@procedures_bp.route('/<int:procedure_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_procedure(procedure_id):
    procedure = Procedure.query.options(
        db.joinedload(Procedure.procedure_material_costs).joinedload(ProcedureMaterialCost.inventory)
    ).get_or_404(procedure_id)

    # Find the logged-in user's corresponding Operator record (if exists)
    user_operator = Operator.query.filter_by(clinic_id=current_user.clinic_id, phone=current_user.phone).first()
    user_operator_id = user_operator.operator_id if user_operator else None

    # Ensure only Admins, Doctors, or the procedure creator can edit
    if current_user.role.role_name not in ["Admin", "Doctor"] and procedure.operator_id != user_operator_id:
        flash("Access denied: You can only edit procedures you created.", "danger")
        return redirect(url_for('procedures.list_procedures'))

    patients = Patient.query.filter_by(clinic_id=current_user.clinic_id).all()
    operators = Operator.query.filter_by(clinic_id=current_user.clinic_id).all()
    procedure_types = ProcedureType.query.all()
    body_regions = BodyRegion.query.all()
    categories = db.session.query(Inventory.category_name).distinct().all()

    if request.method == 'POST':
        procedure.patient_id = request.form['patient_id']
        procedure.operator_id = request.form['operator_id']
        procedure.procedure_type_id = request.form['procedure_type_id']
        procedure.body_region_id = request.form['body_region_id']
        procedure.procedure_date = request.form['procedure_date']
        procedure.price = request.form['price']

        # ✅ Remove existing procedure materials before updating
        ProcedureMaterialCost.query.filter_by(procedure_id=procedure_id).delete()

        # ✅ Add Updated Procedure Materials
        inventory_ids = request.form.getlist('inventory_id')
        material_quantities = request.form.getlist('material_quantity')

        for i in range(len(inventory_ids)):
            if inventory_ids[i] and material_quantities[i]:
                inventory_item = Inventory.query.get(inventory_ids[i])
                quantity_used = float(material_quantities[i])

                if inventory_item.update_stock(quantity_used):
                    procedure_material_cost = ProcedureMaterialCost(
                        procedure_id=procedure.procedure_id,
                        inventory_id=inventory_item.inventory_id,
                        quantity_used=quantity_used,
                        unit=inventory_item.expense.unit
                    )
                    db.session.add(procedure_material_cost)

        db.session.commit()
        flash('Procedure updated successfully!', 'success')
        return redirect(url_for('procedures.list_procedures'))

    return render_template(
        'procedure/edit.html',
        procedure=procedure,
        patients=patients,
        operators=operators,
        procedure_types=procedure_types,
        body_regions=body_regions,
        categories=[c[0] for c in categories]
    )



@procedures_bp.route('/<int:procedure_id>/delete', methods=['POST'])
@login_required
def delete_procedure(procedure_id):
    procedure = Procedure.query.get_or_404(procedure_id)

    # ✅ Find the logged-in user's corresponding Operator record (if exists)
    user_operator = Operator.query.filter_by(clinic_id=current_user.clinic_id, phone=current_user.phone).first()
    user_operator_id = user_operator.operator_id if user_operator else None  # Get the operator_id if found

    # ✅ Ensure only Admins, Doctors, or the procedure creator can delete
    if current_user.role.role_name not in ["Admin", "Doctor"] and procedure.operator_id != user_operator_id:
        flash("Access denied: You can only delete procedures you created.", "danger")
        return redirect(url_for('procedures.list_procedures'))

    db.session.delete(procedure)
    db.session.commit()
    flash('Procedure deleted successfully!', 'success')
    return redirect(url_for('procedures.list_procedures'))

@procedures_bp.route('/get-body-regions/<int:procedure_type_id>')
@login_required
def get_body_regions(procedure_type_id):
    # Fetch all body regions linked to the selected procedure type
    mappings = ProcedureTypeBodyRegion.query.filter_by(procedure_type_id=procedure_type_id).all()
    body_regions = [{"id": mapping.body_region.body_region_id, "name": mapping.body_region.name} for mapping in mappings]

    return jsonify(body_regions)

def calculate_operator_earnings(procedure):
    # Fetch the operator's share details
    operator_share = OperatorShare.query.filter_by(operator_id=procedure.operator_id).first()

    if not operator_share:
        flash(f"No share percentage found for operator {procedure.operator_id}.", "danger")
        return  # Prevent adding incorrect earnings

    # Retrieve percentage shares
    operator_percentage = operator_share.operator_percentage
    clinic_percentage = operator_share.clinic_percentage

    # Ensure procedure price is valid
    if not procedure.price or procedure.price <= 0:
        flash(f"Invalid procedure price for procedure {procedure.procedure_id}. Earnings not calculated.", "danger")
        return

    # Calculate earnings
    operator_earning_amount = (procedure.price * operator_percentage) / 100
    clinic_income_amount = (procedure.price * clinic_percentage) / 100

    # ✅ Store earnings in OperatorEarnings table
    new_operator_earning = OperatorEarnings(
        procedure_id=procedure.procedure_id,
        operator_id=procedure.operator_id,
        revenue=procedure.price,
        operator_share=operator_earning_amount,
        clinic_share=clinic_income_amount
    )
    db.session.add(new_operator_earning)

    # ✅ Store income in ClinicIncome table
    new_clinic_income = ClinicIncome(
        procedure_id=procedure.procedure_id,
        clinic_id=procedure.clinic_id,
        revenue=clinic_income_amount,
        revenue_date=procedure.procedure_date
    )
    db.session.add(new_clinic_income)

    # ✅ Explicitly commit changes
    try:
        db.session.commit()
        flash(f"Earnings recorded: Operator {operator_earning_amount}€, Clinic {clinic_income_amount}€", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error saving earnings: {str(e)}", "danger")


# 📌 Mark a Procedure as Completed and Calculate Earnings
@procedures_bp.route('/<int:procedure_id>/complete', methods=['POST'])
@login_required
def complete_procedure(procedure_id):
    procedure = Procedure.query.get_or_404(procedure_id)

    if procedure.clinic_id != current_user.clinic_id:
        flash("Access denied: This procedure is not in your clinic.", "danger")
        return redirect(url_for('procedures.list_procedures'))

    # ✅ Ensure procedure has a valid price
    if not procedure.price or procedure.price <= 0:
        flash("Procedure must have a valid price before marking it as completed.", "danger")
        return redirect(url_for('procedures.list_procedures'))

    # ✅ Ensure the procedure is not already completed
    if procedure.status == "completed":
        flash("This procedure has already been marked as completed.", "warning")
        return redirect(url_for('procedures.list_procedures'))

    # ✅ Mark procedure as completed
    procedure.status = "completed"
    db.session.commit()

    # ✅ Calculate operator earnings and clinic income
    calculate_operator_earnings(procedure)

    flash('Procedure marked as completed and earnings calculated!', 'success')
    return redirect(url_for('procedures.list_procedures'))

@procedures_bp.route('/get-materials/<category_name>')
@login_required
def get_materials(category_name):
    """Fetch available inventory items for the selected category"""
    inventory_items = Inventory.query.filter(
        Inventory.category_name == category_name,
        Inventory.quantity_available > 0
    ).all()

    materials_list = [{
        "id": item.inventory_id,
        "brand": item.brand,
        "price_per_unit": str(item.price_per_unit),
        "quantity_available": str(item.quantity_available)
    } for item in inventory_items]

    return jsonify(materials_list)


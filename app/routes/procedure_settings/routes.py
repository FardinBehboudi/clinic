from functools import wraps
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.procedure import ProcedureType, BodyRegion, ProcedureTypeBodyRegion
from . import procedure_settings_bp

# 📌 Ensure only Admins or Doctors can modify settings
def admin_or_doctor_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.role.role_name not in ["Admin", "Doctor"]:
            flash("Access denied: Only Admins or Doctors can manage procedure settings.", "danger")
            return redirect(url_for('procedure_settings.list_settings'))
        return func(*args, **kwargs)
    return login_required(wrapper)

# 📌 List All Procedure Settings
@procedure_settings_bp.route('/', methods=['GET'])
@login_required
@admin_or_doctor_required
def list_settings():
    procedure_types = ProcedureType.query.all()
    body_regions = BodyRegion.query.all()
    mappings = ProcedureTypeBodyRegion.query.all()

    return render_template(
        'procedure_settings/list.html',
        procedure_types=procedure_types,
        body_regions=body_regions,
        mappings=mappings  # ✅ Removed `materials`
    )

# 📌 Add Procedure Type
@procedure_settings_bp.route('/procedure-types/add', methods=['GET', 'POST'])
@login_required
@admin_or_doctor_required
def add_procedure_type():
    if request.method == 'POST':
        name = request.form['name']
        new_type = ProcedureType(name=name)
        db.session.add(new_type)
        db.session.commit()
        flash('Procedure Type added successfully!', 'success')
        return redirect(url_for('procedure_settings.list_settings'))
    return render_template('procedure_settings/add_procedure_type.html')

# 📌 Add Body Region
@procedure_settings_bp.route('/body-regions/add', methods=['GET', 'POST'])
@login_required
@admin_or_doctor_required
def add_body_region():
    if request.method == 'POST':
        name = request.form['name']
        new_region = BodyRegion(name=name)
        db.session.add(new_region)
        db.session.commit()
        flash('Body Region added successfully!', 'success')
        return redirect(url_for('procedure_settings.list_settings'))
    return render_template('procedure_settings/add_body_region.html')

# 📌 Map Procedure Type to Body Region
@procedure_settings_bp.route('/procedure-type-body-region/add', methods=['GET', 'POST'])
@login_required
@admin_or_doctor_required
def add_procedure_type_body_region():
    procedure_types = ProcedureType.query.all()
    body_regions = BodyRegion.query.all()

    if request.method == 'POST':
        procedure_type_id = request.form['procedure_type_id']
        body_region_id = request.form['body_region_id']
        new_mapping = ProcedureTypeBodyRegion(procedure_type_id=procedure_type_id, body_region_id=body_region_id)
        db.session.add(new_mapping)
        db.session.commit()
        flash('Procedure Type-Body Region Mapping added successfully!', 'success')
        return redirect(url_for('procedure_settings.list_settings'))

    return render_template('procedure_settings/add_procedure_type_body_region.html', procedure_types=procedure_types, body_regions=body_regions)

# 📌 Edit Procedure Type
@procedure_settings_bp.route('/procedure-types/<int:type_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_or_doctor_required
def edit_procedure_type(type_id):
    procedure_type = ProcedureType.query.get_or_404(type_id)

    if request.method == 'POST':
        procedure_type.name = request.form['name']
        db.session.commit()
        flash('Procedure Type updated successfully!', 'success')
        return redirect(url_for('procedure_settings.list_settings'))

    return render_template('procedure_settings/edit_procedure_type.html', procedure_type=procedure_type)

# 📌 Delete Procedure Type
@procedure_settings_bp.route('/procedure-types/<int:type_id>/delete', methods=['POST'])
@login_required
@admin_or_doctor_required
def delete_procedure_type(type_id):
    procedure_type = ProcedureType.query.get_or_404(type_id)
    db.session.delete(procedure_type)
    db.session.commit()
    flash('Procedure Type deleted successfully!', 'success')
    return redirect(url_for('procedure_settings.list_settings'))

# 📌 Edit Body Region
@procedure_settings_bp.route('/body-regions/<int:region_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_or_doctor_required
def edit_body_region(region_id):
    body_region = BodyRegion.query.get_or_404(region_id)

    if request.method == 'POST':
        body_region.name = request.form['name']
        db.session.commit()
        flash('Body Region updated successfully!', 'success')
        return redirect(url_for('procedure_settings.list_settings'))

    return render_template('procedure_settings/edit_body_region.html', body_region=body_region)

# 📌 Delete Body Region
@procedure_settings_bp.route('/body-regions/<int:region_id>/delete', methods=['POST'])
@login_required
@admin_or_doctor_required
def delete_body_region(region_id):
    body_region = BodyRegion.query.get_or_404(region_id)
    db.session.delete(body_region)
    db.session.commit()
    flash('Body Region deleted successfully!', 'success')
    return redirect(url_for('procedure_settings.list_settings'))

# 📌 Edit Procedure Type-Body Region Mapping
@procedure_settings_bp.route('/procedure-type-body-region/<int:mapping_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_or_doctor_required
def edit_procedure_type_body_region(mapping_id):
    mapping = ProcedureTypeBodyRegion.query.get_or_404(mapping_id)
    procedure_types = ProcedureType.query.all()
    body_regions = BodyRegion.query.all()

    if request.method == 'POST':
        mapping.procedure_type_id = request.form['procedure_type_id']
        mapping.body_region_id = request.form['body_region_id']
        db.session.commit()
        flash('Procedure Type-Body Region Mapping updated successfully!', 'success')
        return redirect(url_for('procedure_settings.list_settings'))

    return render_template('procedure_settings/edit_procedure_type_body_region.html', mapping=mapping, procedure_types=procedure_types, body_regions=body_regions)

# 📌 Delete Procedure Type-Body Region Mapping
@procedure_settings_bp.route('/procedure-type-body-region/<int:mapping_id>/delete', methods=['POST'])
@login_required
@admin_or_doctor_required
def delete_procedure_type_body_region(mapping_id):
    mapping = ProcedureTypeBodyRegion.query.get_or_404(mapping_id)
    db.session.delete(mapping)
    db.session.commit()
    flash('Procedure Type-Body Region Mapping deleted successfully!', 'success')
    return redirect(url_for('procedure_settings.list_settings'))

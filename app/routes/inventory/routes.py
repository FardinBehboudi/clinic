from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.expense import Inventory
from app.routes.inventory import inventory_bp


@inventory_bp.route("/", methods=["GET"])
@login_required
def view_inventory():
    """Show all inventory items for the clinic"""
    inventory_items = Inventory.query.filter(
        Inventory.expense.has(clinic_id=current_user.clinic_id)
    ).all()

    return render_template("inventory/list.html", inventory_items=inventory_items)

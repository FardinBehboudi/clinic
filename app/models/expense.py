from datetime import datetime
from decimal import Decimal

from app.extensions import db

class ExpenseType(db.Model):
    expense_type_id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(100), unique=True, nullable=False)

class ExpenseCategory(db.Model):
    expense_category_id = db.Column(db.Integer, primary_key=True)
    expense_type_id = db.Column(db.Integer, db.ForeignKey('expense_type.expense_type_id', ondelete="CASCADE"), nullable=False)
    category_name = db.Column(db.String(100), nullable=False)

    expense_type = db.relationship("ExpenseType", backref="categories")


class Expenses(db.Model):
    expense_id = db.Column(db.Integer, primary_key=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinic.clinic_id', ondelete="CASCADE"), nullable=False)
    expense_type_id = db.Column(db.Integer, db.ForeignKey('expense_type.expense_type_id', ondelete="CASCADE"),
                                nullable=False)
    expense_category_id = db.Column(db.Integer,
                                    db.ForeignKey('expense_category.expense_category_id', ondelete="CASCADE"),
                                    nullable=False)
    brand = db.Column(db.String(255))
    quantity = db.Column(db.Integer, nullable=True)  # ✅ Allow NULL quantity
    unit = db.Column(db.String(50))
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    price_per_unit = db.Column(db.Numeric(10, 2), nullable=True, default=None)
    purchase_date = db.Column(db.Date, nullable=False)
    provider = db.Column(db.String(255))

    # ✅ Relationships
    expense_type = db.relationship("ExpenseType", backref="expenses")
    expense_category = db.relationship("ExpenseCategory", backref="expenses")

    # ✅ Automatically calculate price per unit before inserting or updating
    @staticmethod
    def calculate_price_per_unit(target):
        try:
            total_price = float(target.total_price)  # ✅ Ensure total_price is a float
            quantity = int(target.quantity) if target.quantity else None  # ✅ Convert quantity or set None

            if quantity and quantity > 0:
                target.price_per_unit = total_price / quantity
            else:
                target.price_per_unit = None
        except (ValueError, TypeError):
            target.price_per_unit = None  # ✅ Handle invalid data


# ✅ Listen for changes to recalculate price per unit
from sqlalchemy.event import listens_for


@listens_for(Expenses, "before_insert")
@listens_for(Expenses, "before_update")
def before_insert_or_update(mapper, connection, target):
    Expenses.calculate_price_per_unit(target)

class Inventory(db.Model):
    inventory_id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer, db.ForeignKey('expenses.expense_id', ondelete="CASCADE"), nullable=False)
    category_name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    price_per_unit = db.Column(db.Numeric(10, 2), nullable=False)
    quantity_available = db.Column(db.Numeric(10, 2), nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ✅ Relationships
    expense = db.relationship("Expenses", backref="inventory_items")

    def update_stock(self, quantity_used):
        """Deduct used materials from inventory"""
        quantity_used_decimal = Decimal(str(quantity_used))  # ✅ Convert to Decimal
        if self.quantity_available >= quantity_used_decimal:
            self.quantity_available -= quantity_used_decimal
            db.session.commit()
            return True
        return False  # Not enough stock

class ProcedureMaterialCost(db.Model):
    procedure_material_cost_id = db.Column(db.Integer, primary_key=True)
    procedure_id = db.Column(db.Integer, db.ForeignKey('procedure.procedure_id', ondelete="CASCADE"), nullable=False)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.inventory_id', ondelete="CASCADE"), nullable=False)
    quantity_used = db.Column(db.Numeric(10, 2), nullable=False)
    unit = db.Column(db.String(50), nullable=False)

    # ✅ Use a unique backref name
    procedure = db.relationship("Procedure", backref="materials_used", cascade="all, delete")
    inventory = db.relationship("Inventory", backref="used_in_procedures")
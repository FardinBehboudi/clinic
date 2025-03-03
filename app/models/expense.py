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


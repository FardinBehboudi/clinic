from app.extensions import db

class ExpenseType(db.Model):
    expense_type_id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(100), unique=True, nullable=False)

class ExpenseCategory(db.Model):
    expense_category_id = db.Column(db.Integer, primary_key=True)
    expense_type_id = db.Column(db.Integer, db.ForeignKey('expense_type.expense_type_id', ondelete="CASCADE"), nullable=False)
    category_name = db.Column(db.String(100), nullable=False)

class Expenses(db.Model):
    expense_id = db.Column(db.Integer, primary_key=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinic.clinic_id', ondelete="CASCADE"), nullable=False)
    expense_type_id = db.Column(db.Integer, db.ForeignKey('expense_type.expense_type_id', ondelete="CASCADE"), nullable=False)
    expense_category_id = db.Column(db.Integer, db.ForeignKey('expense_category.expense_category_id', ondelete="CASCADE"), nullable=False)
    brand = db.Column(db.String(255))
    quantity = db.Column(db.Integer, default=1)
    unit = db.Column(db.String(50))
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    provider = db.Column(db.String(255))

from app.extensions import db

class Income(db.Model):
    income_id = db.Column(db.Integer, primary_key=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinic.clinic_id', ondelete="CASCADE"), nullable=False)
    procedure_id = db.Column(db.Integer, db.ForeignKey('procedure.procedure_id', ondelete="CASCADE"), nullable=False)
    revenue = db.Column(db.Numeric(10, 2), nullable=False)

class OperatorShare(db.Model):
    share_id = db.Column(db.Integer, primary_key=True)
    operator_id = db.Column(db.Integer, db.ForeignKey('operator.operator_id', ondelete="CASCADE"), nullable=False)
    clinic_percentage = db.Column(db.Numeric(5, 2), nullable=False)
    operator_percentage = db.Column(db.Numeric(5, 2), nullable=False)

class OperatorEarnings(db.Model):
    earning_id = db.Column(db.Integer, primary_key=True)
    procedure_id = db.Column(db.Integer, db.ForeignKey('procedure.procedure_id', ondelete="CASCADE"), nullable=False)
    operator_id = db.Column(db.Integer, db.ForeignKey('operator.operator_id', ondelete="CASCADE"), nullable=False)
    revenue = db.Column(db.Numeric(10, 2), nullable=False)
    clinic_share = db.Column(db.Numeric(10, 2), nullable=False)
    operator_share = db.Column(db.Numeric(10, 2), nullable=False)

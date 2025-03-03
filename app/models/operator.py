from app.extensions import db

class Operator(db.Model):
    operator_id = db.Column(db.Integer, primary_key=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinic.clinic_id', ondelete="CASCADE"), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    specialty = db.Column(db.String(255))
    experience_years = db.Column(db.Integer)

    operator_shares = db.relationship("OperatorShare", back_populates="operator", cascade="all, delete-orphan")

    clinic = db.relationship('Clinic', backref='operators')

class OperatorHistory(db.Model):
    history_id = db.Column(db.Integer, primary_key=True)
    operator_id = db.Column(db.Integer, db.ForeignKey('operator.operator_id', ondelete="CASCADE"), nullable=False)
    procedure_id = db.Column(db.Integer, db.ForeignKey('procedure.procedure_id', ondelete="CASCADE"), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.patient_id', ondelete="CASCADE"), nullable=False)
    procedure_date = db.Column(db.Date, nullable=False)

    operator = db.relationship('Operator', backref='operator_history')  # ✅ Updated backref name
    procedure = db.relationship('Procedure', backref='operator_history')
    patient = db.relationship('Patient', backref='operator_history')  # ✅ Updated backref name

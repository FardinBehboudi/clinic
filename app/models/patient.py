from app.extensions import db

class Patient(db.Model):
    patient_id = db.Column(db.Integer, primary_key=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinic.clinic_id', ondelete="CASCADE"), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(255), nullable=True)  # ✅ Email Can Be Null or Duplicate
    date_of_birth = db.Column(db.Date)
    medical_history = db.Column(db.Text)

    clinic = db.relationship('Clinic', backref='patients')

    __table_args__ = (db.UniqueConstraint('clinic_id', 'phone', name='unique_clinic_phone'),)  # ✅ Unique Constraint for (clinic_id, phone)

class PatientHistory(db.Model):
    history_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.patient_id', ondelete="CASCADE"), nullable=False)
    procedure_id = db.Column(db.Integer, db.ForeignKey('procedure.procedure_id', ondelete="CASCADE"), nullable=False)
    operator_id = db.Column(db.Integer, db.ForeignKey('operator.operator_id', ondelete="CASCADE"), nullable=False)

    patient = db.relationship('Patient', backref='patient_history')  # ✅ Updated backref name
    procedure = db.relationship('Procedure', backref='patient_history')
    operator = db.relationship('Operator', backref='patient_history')  # ✅ Updated backref name

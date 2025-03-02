from app.extensions import db

class AppointmentStatus(db.Model):
    status_id = db.Column(db.Integer, primary_key=True)
    status_name = db.Column(db.String(50), unique=True, nullable=False)

class Appointment(db.Model):
    appointment_id = db.Column(db.Integer, primary_key=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinic.clinic_id', ondelete="CASCADE"), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.patient_id', ondelete="CASCADE"), nullable=False)
    operator_id = db.Column(db.Integer, db.ForeignKey('operator.operator_id', ondelete="CASCADE"), nullable=False)
    procedure_type_id = db.Column(db.Integer, db.ForeignKey('procedure_type.procedure_type_id', ondelete="CASCADE"), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_title = db.Column(db.String(255), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('appointment_status.status_id', ondelete="CASCADE"), nullable=False)
    note = db.Column(db.Text)

    clinic = db.relationship('Clinic', backref='appointments')
    patient = db.relationship('Patient', backref='appointments')
    operator = db.relationship('Operator', backref='appointments')
    procedure_type = db.relationship('ProcedureType', backref='appointments')
    status = db.relationship('AppointmentStatus', backref='appointments')

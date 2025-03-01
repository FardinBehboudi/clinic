from app.extensions import db

class Patient(db.Model):
    patient_id = db.Column(db.Integer, primary_key=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinic.clinic_id', ondelete="CASCADE"), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True)
    date_of_birth = db.Column(db.Date)
    medical_history = db.Column(db.Text)

    clinic = db.relationship('Clinic', backref='patients')

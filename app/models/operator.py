from app.extensions import db

class Operator(db.Model):
    operator_id = db.Column(db.Integer, primary_key=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinic.clinic_id', ondelete="CASCADE"), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    specialty = db.Column(db.String(255))
    experience_years = db.Column(db.Integer)

    clinic = db.relationship('Clinic', backref='operators')

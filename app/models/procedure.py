from app.extensions import db

class ProcedureType(db.Model):
    procedure_type_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class BodyRegion(db.Model):
    body_region_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class ProcedureTypeBodyRegion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    procedure_type_id = db.Column(db.Integer, db.ForeignKey('procedure_type.procedure_type_id', ondelete="CASCADE"), nullable=False)
    body_region_id = db.Column(db.Integer, db.ForeignKey('body_region.body_region_id', ondelete="CASCADE"), nullable=False)

class Procedure(db.Model):
    procedure_id = db.Column(db.Integer, primary_key=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinic.clinic_id', ondelete="CASCADE"), nullable=False)
    operator_id = db.Column(db.Integer, db.ForeignKey('operator.operator_id', ondelete="CASCADE"), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.patient_id', ondelete="CASCADE"), nullable=False)
    procedure_type_id = db.Column(db.Integer, db.ForeignKey('procedure_type.procedure_type_id', ondelete="CASCADE"), nullable=False)
    body_region_id = db.Column(db.Integer, db.ForeignKey('body_region.body_region_id', ondelete="CASCADE"), nullable=False)
    brand = db.Column(db.String(255))
    procedure_date = db.Column(db.Date, nullable=False)

    clinic = db.relationship('Clinic', backref='procedures')
    operator = db.relationship('Operator', backref='procedures')
    patient = db.relationship('Patient', backref='procedures')
    procedure_type = db.relationship('ProcedureType', backref='procedures')
    body_region = db.relationship('BodyRegion', backref='procedures')

class ProcedureMaterial(db.Model):
    procedure_material_id = db.Column(db.Integer, primary_key=True)
    procedure_id = db.Column(db.Integer, db.ForeignKey('procedure.procedure_id', ondelete="CASCADE"), nullable=False)
    expense_id = db.Column(db.Integer, db.ForeignKey('expenses.expense_id', ondelete="CASCADE"), nullable=False)
    quantity_used = db.Column(db.Numeric(10,2), nullable=False)
    unit = db.Column(db.String(50), nullable=False)

class PatientHistory(db.Model):
    history_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.patient_id', ondelete="CASCADE"), nullable=False)
    procedure_id = db.Column(db.Integer, db.ForeignKey('procedure.procedure_id', ondelete="CASCADE"), nullable=False)
    operator_id = db.Column(db.Integer, db.ForeignKey('operator.operator_id', ondelete="CASCADE"), nullable=False)
    revenue = db.Column(db.Numeric(10,2), nullable=False)
    procedure_date = db.Column(db.Date, nullable=False)

    patient = db.relationship('Patient', backref='history')
    procedure = db.relationship('Procedure', backref='history')
    operator = db.relationship('Operator', backref='history')

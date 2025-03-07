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

    # ✅ Establish Relationships
    procedure_type = db.relationship("ProcedureType", backref="type_body_regions")
    body_region = db.relationship("BodyRegion", backref="region_procedure_types")

class Procedure(db.Model):
    procedure_id = db.Column(db.Integer, primary_key=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinic.clinic_id', ondelete="CASCADE"), nullable=False)
    operator_id = db.Column(db.Integer, db.ForeignKey('operator.operator_id', ondelete="CASCADE"), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.patient_id', ondelete="CASCADE"), nullable=False)
    procedure_type_id = db.Column(db.Integer, db.ForeignKey('procedure_type.procedure_type_id', ondelete="CASCADE"), nullable=False)
    body_region_id = db.Column(db.Integer, db.ForeignKey('body_region.body_region_id', ondelete="CASCADE"), nullable=False)
    procedure_date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Numeric(10,2), nullable=False)
    status = db.Column(db.String(20), default="pending")

    clinic = db.relationship('Clinic', backref='procedures')
    operator = db.relationship('Operator', backref='procedures')
    patient = db.relationship('Patient', backref='procedures')
    procedure_type = db.relationship('ProcedureType', backref='procedures')
    body_region = db.relationship('BodyRegion', backref='procedures')

    # ✅ Ensure this matches the ProcedureMaterialCost model
    procedure_material_costs = db.relationship(
        "ProcedureMaterialCost",
        back_populates="procedure",
        cascade="all, delete",
        overlaps="materials_used"
    )
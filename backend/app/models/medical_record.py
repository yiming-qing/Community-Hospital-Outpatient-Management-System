from __future__ import annotations

from ..extensions import db


class MedicalRecord(db.Model):
    __tablename__ = "medical_record"

    record_id = db.Column(db.Integer, primary_key=True)
    visit_id = db.Column(db.Integer, db.ForeignKey("visit.visit_id"), nullable=False, unique=True)

    diagnosis = db.Column(db.Text)
    treatment = db.Column(db.Text)
    prescription = db.Column(db.Text)
    note = db.Column(db.Text)

    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        nullable=False,
        onupdate=db.func.current_timestamp(),
    )

    visit = db.relationship("Visit", lazy="joined")

    def to_dict(self):
        return {
            "record_id": self.record_id,
            "visit_id": self.visit_id,
            "diagnosis": self.diagnosis,
            "treatment": self.treatment,
            "prescription": self.prescription,
            "note": self.note,
            "created_at": self.created_at.isoformat(sep=" ", timespec="seconds") if self.created_at else None,
            "updated_at": self.updated_at.isoformat(sep=" ", timespec="seconds") if self.updated_at else None,
        }


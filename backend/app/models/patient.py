from __future__ import annotations

from ..extensions import db


class Patient(db.Model):
    __tablename__ = "patient"

    patient_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.Enum("男", "女", validate_strings=True))
    id_card = db.Column(db.String(18), unique=True)
    phone = db.Column(db.String(20), nullable=False, index=True)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), nullable=False)

    def to_dict(self):
        return {
            "patient_id": self.patient_id,
            "name": self.name,
            "gender": self.gender,
            "id_card": self.id_card,
            "phone": self.phone,
        }


from __future__ import annotations

from ..extensions import db


class PatientUser(db.Model):
    __tablename__ = "patient_user"

    user_id = db.Column(db.Integer, db.ForeignKey("sys_user.user_id"), primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.patient_id"), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), nullable=False)

    user = db.relationship("SysUser", back_populates="patient_link", lazy="joined")
    patient = db.relationship("Patient", lazy="joined")


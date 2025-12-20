from __future__ import annotations

from ..extensions import db


class Visit(db.Model):
    __tablename__ = "visit"

    visit_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.patient_id"), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey("room.room_id"), nullable=False)
    doctor_id = db.Column(db.String(20), db.ForeignKey("employee.emp_id"))
    appt_id = db.Column(db.Integer, db.ForeignKey("appointment.appt_id"), unique=True)
    status = db.Column(
        db.Enum("候诊中", "就诊中", "待缴费", "已离院", validate_strings=True),
        nullable=False,
        server_default="候诊中",
    )
    check_in_time = db.Column(db.DateTime, server_default=db.func.current_timestamp(), nullable=False)
    checkout_time = db.Column(db.DateTime)

    patient = db.relationship("Patient", lazy="joined")
    room = db.relationship("Room", lazy="joined")
    doctor = db.relationship("Employee", lazy="joined")
    appointment = db.relationship("Appointment", lazy="joined")

    def to_dict(self):
        return {
            "visit_id": self.visit_id,
            "patient": self.patient.to_dict() if self.patient else None,
            "room": self.room.to_dict() if self.room else None,
            "doctor": self.doctor.to_dict() if self.doctor else None,
            "appt_id": self.appt_id,
            "status": self.status,
            "check_in_time": self.check_in_time.isoformat(sep=" ", timespec="seconds")
            if self.check_in_time
            else None,
            "checkout_time": self.checkout_time.isoformat(sep=" ", timespec="seconds")
            if self.checkout_time
            else None,
        }

from __future__ import annotations

from ..extensions import db


class Appointment(db.Model):
    __tablename__ = "appointment"

    appt_id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False, index=True)
    dept_id = db.Column(db.Integer, db.ForeignKey("department.dept_id"), nullable=False)
    expected_time = db.Column(db.DateTime, nullable=False, index=True)
    status = db.Column(
        db.Enum("待确认", "已确认", "已完成", "已取消", validate_strings=True),
        nullable=False,
        server_default="待确认",
    )
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.patient_id"))
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), nullable=False)

    department = db.relationship("Department", lazy="joined")
    patient = db.relationship("Patient", lazy="joined")

    def to_dict(self):
        return {
            "appt_id": self.appt_id,
            "patient_name": self.patient_name,
            "phone": self.phone,
            "dept_id": self.dept_id,
            "dept_name": self.department.dept_name if self.department else None,
            "expected_time": self.expected_time.isoformat(sep=" ", timespec="seconds"),
            "status": self.status,
            "patient_id": self.patient_id,
        }

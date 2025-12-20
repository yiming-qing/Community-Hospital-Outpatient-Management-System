from __future__ import annotations

from ..extensions import db


class Schedule(db.Model):
    __tablename__ = "schedule"
    __table_args__ = (db.UniqueConstraint("room_id", "work_date", "time_slot", name="uniq_room_date_slot"),)

    schedule_id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("room.room_id"), nullable=False)
    doctor_id = db.Column(db.String(20), db.ForeignKey("employee.emp_id"), nullable=False)
    work_date = db.Column(db.Date, nullable=False)
    time_slot = db.Column(db.Enum("上午", "下午", "全天", validate_strings=True), nullable=False)
    max_patients = db.Column(db.Integer, nullable=False, server_default="30")
    current_patients = db.Column(db.Integer, nullable=False, server_default="0")

    room = db.relationship("Room", lazy="joined")
    doctor = db.relationship("Employee", lazy="joined")

    def to_dict(self):
        return {
            "schedule_id": self.schedule_id,
            "room_id": self.room_id,
            "room_number": self.room.room_number if self.room else None,
            "dept_id": self.room.dept_id if self.room else None,
            "dept_name": self.room.department.dept_name if self.room and self.room.department else None,
            "doctor_id": self.doctor_id,
            "doctor_name": self.doctor.name if self.doctor else None,
            "work_date": self.work_date.isoformat(),
            "time_slot": self.time_slot,
            "max_patients": self.max_patients,
            "current_patients": self.current_patients,
        }

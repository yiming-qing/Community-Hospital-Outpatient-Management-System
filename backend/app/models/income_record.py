from __future__ import annotations

from ..extensions import db


class IncomeRecord(db.Model):
    __tablename__ = "income_record"

    record_id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey("bill.bill_id"), nullable=False)
    dept_id = db.Column(db.Integer, db.ForeignKey("department.dept_id"), nullable=False)
    doctor_id = db.Column(db.String(20), db.ForeignKey("employee.emp_id"))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    record_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), nullable=False)

    department = db.relationship("Department", lazy="joined")
    doctor = db.relationship("Employee", lazy="joined")

    def to_dict(self):
        return {
            "record_id": self.record_id,
            "bill_id": self.bill_id,
            "dept_id": self.dept_id,
            "dept_name": self.department.dept_name if self.department else None,
            "doctor_id": self.doctor_id,
            "doctor_name": self.doctor.name if self.doctor else None,
            "amount": float(self.amount),
            "record_date": self.record_date.isoformat(),
        }


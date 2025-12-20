from __future__ import annotations

from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db


class SysUser(db.Model):
    __tablename__ = "sys_user"

    user_id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(20), db.ForeignKey("employee.emp_id"))
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("patient", "receptionist", "admin", validate_strings=True), nullable=False)
    status = db.Column(db.Enum("active", "inactive", validate_strings=True), nullable=False, server_default="active")
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), nullable=False)

    employee = db.relationship("Employee", lazy="joined")
    patient_link = db.relationship("PatientUser", back_populates="user", uselist=False, lazy="joined")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_safe_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "role": self.role,
            "status": self.status,
            "emp_id": self.emp_id,
            "employee": self.employee.to_dict() if self.employee else None,
            "patient_id": self.patient_link.patient_id if self.patient_link else None,
            "patient": self.patient_link.patient.to_dict() if self.patient_link and self.patient_link.patient else None,
        }

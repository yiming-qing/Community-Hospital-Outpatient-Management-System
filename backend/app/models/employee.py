from __future__ import annotations

from ..extensions import db


class Employee(db.Model):
    __tablename__ = "employee"

    emp_id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.Enum("男", "女", validate_strings=True), nullable=False)
    phone = db.Column(db.String(20))
    position = db.Column(db.Enum("医生", "护士", "前台", "管理员", validate_strings=True), nullable=False)
    title = db.Column(db.String(50))
    dept_id = db.Column(db.Integer, db.ForeignKey("department.dept_id"))
    status = db.Column(
        db.Enum("在职", "离职", "休假", validate_strings=True),
        nullable=False,
        server_default="在职",
    )
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), nullable=False)

    department = db.relationship("Department", lazy="joined")

    def to_dict(self):
        return {
            "emp_id": self.emp_id,
            "name": self.name,
            "gender": self.gender,
            "phone": self.phone,
            "position": self.position,
            "title": self.title,
            "dept_id": self.dept_id,
            "dept_name": self.department.dept_name if self.department else None,
            "status": self.status,
        }

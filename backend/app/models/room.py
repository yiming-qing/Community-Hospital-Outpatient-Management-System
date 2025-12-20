from __future__ import annotations

from ..extensions import db


class Room(db.Model):
    __tablename__ = "room"

    room_id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(20), nullable=False, unique=True)
    dept_id = db.Column(db.Integer, db.ForeignKey("department.dept_id"), nullable=False)
    status = db.Column(db.Enum("启用", "停用", validate_strings=True), nullable=False, server_default="启用")

    department = db.relationship("Department", lazy="joined")

    def to_dict(self):
        return {
            "room_id": self.room_id,
            "room_number": self.room_number,
            "dept_id": self.dept_id,
            "dept_name": self.department.dept_name if self.department else None,
            "status": self.status,
        }

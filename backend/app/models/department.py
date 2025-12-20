from __future__ import annotations

from ..extensions import db


class Department(db.Model):
    __tablename__ = "department"

    dept_id = db.Column(db.Integer, primary_key=True)
    dept_name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), nullable=False)

    def to_dict(self):
        return {
            "dept_id": self.dept_id,
            "dept_name": self.dept_name,
            "description": self.description,
        }


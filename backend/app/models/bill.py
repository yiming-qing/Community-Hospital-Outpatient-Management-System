from __future__ import annotations

from ..extensions import db


class Bill(db.Model):
    __tablename__ = "bill"

    bill_id = db.Column(db.Integer, primary_key=True)
    visit_id = db.Column(db.Integer, db.ForeignKey("visit.visit_id"), nullable=False, unique=True)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, server_default="0.00")
    insurance_amount = db.Column(db.Numeric(10, 2), nullable=False, server_default="0.00")
    self_pay_amount = db.Column(db.Numeric(10, 2), nullable=False, server_default="0.00")
    pay_status = db.Column(db.Enum("未支付", "已支付", validate_strings=True), nullable=False, server_default="未支付")
    pay_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), nullable=False)

    visit = db.relationship("Visit", lazy="joined")

    def to_dict(self):
        return {
            "bill_id": self.bill_id,
            "visit_id": self.visit_id,
            "total_amount": float(self.total_amount),
            "insurance_amount": float(self.insurance_amount),
            "self_pay_amount": float(self.self_pay_amount),
            "pay_status": self.pay_status,
            "pay_time": self.pay_time.isoformat(sep=" ", timespec="seconds") if self.pay_time else None,
        }

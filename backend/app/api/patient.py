from __future__ import annotations

from flask import Blueprint, request

from ..extensions import db
from ..models import Appointment, Department, Patient
from ..utils.auth import roles_required
from ..utils.datetime_utils import parse_datetime
from ..utils.errors import APIError
from ..utils.responses import ok

bp = Blueprint("patient", __name__, url_prefix="/api/patient")


@bp.get("/departments")
def list_departments():
    departments = Department.query.order_by(Department.dept_id.asc()).all()
    return ok([d.to_dict() for d in departments])


@bp.post("/appointments")
@roles_required("patient")
def create_appointment():
    payload = request.get_json(silent=True) or {}
    dept_id = payload.get("dept_id")
    expected_time = parse_datetime(payload.get("expected_time") or "")

    if not dept_id:
        raise APIError(
            "dept_id is required",
            code="validation_error",
            status=400,
        )

    department = Department.query.get(dept_id)
    if department is None:
        raise APIError("Invalid dept_id", code="validation_error", status=400)

    from flask_jwt_extended import current_user

    if current_user is None or getattr(current_user, "patient_link", None) is None:
        raise APIError("Unauthorized", code="unauthorized", status=401)
    patient: Patient | None = current_user.patient_link.patient  # type: ignore[assignment]
    if patient is None:
        raise APIError("Unauthorized", code="unauthorized", status=401)

    appt = Appointment(
        patient_name=patient.name,
        phone=patient.phone,
        dept_id=dept_id,
        expected_time=expected_time,
        status="待确认",
        patient_id=patient.patient_id,
    )
    db.session.add(appt)
    db.session.commit()

    return ok(appt.to_dict(), status=201)


@bp.get("/appointments/query")
@roles_required("patient")
def query_appointments():
    from flask_jwt_extended import current_user

    if current_user is None or getattr(current_user, "patient_link", None) is None:
        raise APIError("Unauthorized", code="unauthorized", status=401)
    patient: Patient | None = current_user.patient_link.patient  # type: ignore[assignment]
    if patient is None:
        raise APIError("Unauthorized", code="unauthorized", status=401)

    q = Appointment.query.filter_by(patient_id=patient.patient_id).order_by(Appointment.appt_id.desc())
    status = (request.args.get("status") or "").strip()
    if status:
        q = q.filter(Appointment.status == status)

    appts = q.limit(50).all()
    return ok([a.to_dict() for a in appts])


@bp.delete("/appointments/<int:appt_id>")
@roles_required("patient")
def cancel_appointment(appt_id: int):
    from flask_jwt_extended import current_user

    if current_user is None or getattr(current_user, "patient_link", None) is None:
        raise APIError("Unauthorized", code="unauthorized", status=401)
    patient: Patient | None = current_user.patient_link.patient  # type: ignore[assignment]
    if patient is None:
        raise APIError("Unauthorized", code="unauthorized", status=401)

    appt = Appointment.query.get(appt_id)
    if appt is None or appt.patient_id != patient.patient_id:
        raise APIError("Appointment not found", code="not_found", status=404)

    if appt.status in ("已完成", "已取消"):
        return ok(appt.to_dict())

    appt.status = "已取消"
    db.session.commit()
    return ok(appt.to_dict())

from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal, ROUND_HALF_UP

from flask import Blueprint, request

from ..extensions import db
from ..models import Appointment, Bill, IncomeRecord, Patient, Room, Schedule, Visit
from ..utils.auth import roles_required
from ..utils.datetime_utils import detect_time_slot, parse_date, parse_datetime
from ..utils.errors import APIError
from ..utils.responses import ok

bp = Blueprint("receptionist", __name__, url_prefix="/api/receptionist")

_MONEY_CENT = Decimal("0.01")


def _parse_money(value, *, field: str) -> Decimal:
    try:
        d = Decimal(str(value))
    except Exception as e:
        raise APIError("Invalid amount", code="validation_error", status=400, details={"field": field}) from e
    if d.is_nan() or d.is_infinite():
        raise APIError("Invalid amount", code="validation_error", status=400, details={"field": field})
    return d.quantize(_MONEY_CENT, rounding=ROUND_HALF_UP)


def _parse_int(value: str | None, *, field: str) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except Exception as e:
        raise APIError(f"Invalid {field}", code="validation_error", status=400) from e


def _reserve_schedule(*, dept_id: int, target_dt: datetime) -> Schedule:
    slot = detect_time_slot(target_dt)
    work_date = target_dt.date()

    q = (
        Schedule.query.join(Room, Schedule.room_id == Room.room_id)
        .filter(Room.dept_id == dept_id)
        .filter(Room.status == "启用")
        .filter(Schedule.work_date == work_date)
        .filter(Schedule.time_slot.in_([slot, "全天"]))
        .filter(Schedule.current_patients < Schedule.max_patients)
        .order_by(Schedule.current_patients.asc(), Schedule.schedule_id.asc())
    )
    schedule_ids = [sid for (sid,) in q.with_entities(Schedule.schedule_id).limit(20).all()]
    for schedule_id in schedule_ids:
        updated = (
            Schedule.query.filter(Schedule.schedule_id == schedule_id)
            .filter(Schedule.current_patients < Schedule.max_patients)
            .update({Schedule.current_patients: Schedule.current_patients + 1}, synchronize_session=False)
        )
        if updated:
            schedule = Schedule.query.get(schedule_id)
            if schedule is None:
                raise APIError("Schedule not found", code="invalid_state", status=409)
            return schedule

    raise APIError("No available schedule for this department/time", code="no_schedule", status=409)


def _get_or_create_patient(*, name: str, phone: str, gender: str | None, id_card: str | None) -> Patient:
    patient = None
    if id_card:
        patient = Patient.query.filter_by(id_card=id_card).first()
    if patient is None:
        patient = (
            Patient.query.filter_by(phone=phone, name=name).order_by(Patient.patient_id.desc()).first()
        )
    if patient is None:
        patient = Patient(name=name, phone=phone, gender=gender, id_card=id_card)
        db.session.add(patient)
        db.session.flush()
        return patient

    if id_card and not patient.id_card:
        patient.id_card = id_card
    if gender and not patient.gender:
        patient.gender = gender
    return patient


@bp.get("/appointments")
@roles_required("receptionist")
def list_appointments():
    q = Appointment.query.order_by(Appointment.appt_id.desc())
    status = (request.args.get("status") or "").strip()
    if status:
        q = q.filter(Appointment.status == status)
    appts = q.limit(100).all()
    return ok([a.to_dict() for a in appts])


_APPOINTMENT_TRANSITIONS: dict[str, set[str]] = {
    "待确认": {"已确认", "已取消"},
    "已确认": {"已取消"},
    "已完成": set(),
    "已取消": set(),
}


@bp.put("/appointments/<int:appt_id>/status")
@roles_required("receptionist")
def update_appointment_status(appt_id: int):
    payload = request.get_json(silent=True) or {}
    new_status = (payload.get("status") or "").strip()
    if not new_status:
        raise APIError("status is required", code="validation_error", status=400)

    if new_status not in ("待确认", "已确认", "已完成", "已取消"):
        raise APIError("Invalid status", code="validation_error", status=400)

    appt = Appointment.query.get(appt_id)
    if appt is None:
        raise APIError("Appointment not found", code="not_found", status=404)

    allowed = _APPOINTMENT_TRANSITIONS.get(appt.status, set())
    if new_status not in allowed:
        raise APIError(
            "Invalid status transition",
            code="invalid_state",
            status=409,
            details={"from": appt.status, "to": new_status, "allowed": sorted(allowed)},
        )

    appt.status = new_status
    db.session.commit()
    return ok(appt.to_dict())


@bp.post("/checkin/<int:appt_id>")
@roles_required("receptionist")
def checkin(appt_id: int):
    payload = request.get_json(silent=True) or {}
    phone = (payload.get("phone") or "").strip()
    id_card = (payload.get("id_card") or "").strip() or None

    try:
        appt = Appointment.query.get(appt_id)
        if appt is None:
            raise APIError("Appointment not found", code="not_found", status=404)
        existing_visit = Visit.query.filter_by(appt_id=appt_id).first()
        if existing_visit is not None:
            raise APIError("Appointment already checked in", code="invalid_state", status=409)
        if phone and appt.phone != phone:
            raise APIError("Phone does not match appointment", code="validation_error", status=400)
        if appt.status in ("已完成", "已取消"):
            raise APIError(f"Appointment status is {appt.status}", code="invalid_state", status=409)

        schedule = _reserve_schedule(dept_id=appt.dept_id, target_dt=appt.expected_time)

        patient = appt.patient
        if patient is None:
            patient = _get_or_create_patient(
                name=appt.patient_name,
                phone=appt.phone,
                gender=None,
                id_card=id_card,
            )
            appt.patient_id = patient.patient_id
        else:
            if id_card and patient.id_card and patient.id_card != id_card:
                raise APIError("id_card does not match", code="validation_error", status=400)
            if id_card and not patient.id_card:
                patient.id_card = id_card

        visit = Visit(
            patient_id=patient.patient_id,
            room_id=schedule.room_id,
            doctor_id=schedule.doctor_id,
            appt_id=appt.appt_id,
            status="候诊中",
        )
        db.session.add(visit)
        appt.status = "已完成"

        db.session.flush()
        visit_data = visit.to_dict()
        db.session.commit()
        return ok(visit_data, status=201)
    except APIError:
        db.session.rollback()
        raise
    except Exception:
        db.session.rollback()
        raise


@bp.post("/register")
@roles_required("receptionist")
def onsite_register():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    phone = (payload.get("phone") or "").strip()
    dept_id = payload.get("dept_id")
    gender = (payload.get("gender") or "").strip() or None
    id_card = (payload.get("id_card") or "").strip() or None

    if not name or not phone or not dept_id:
        raise APIError("name, phone, dept_id are required", code="validation_error", status=400)
    if gender is not None and gender not in ("男", "女"):
        raise APIError("Invalid gender", code="validation_error", status=400)

    raw_expected = payload.get("expected_time") or datetime.now().isoformat(sep=" ", timespec="seconds")
    target_dt = parse_datetime(raw_expected)
    from datetime import timedelta

    # ✅ 核心：不允许现场挂号选择过去时间（给 30 秒容忍，避免前后端时钟微小偏差）
    if target_dt < datetime.now() - timedelta(seconds=30):
        raise APIError("不能预约过去的时间", code="validation_error", status=400)

    try:
        schedule = _reserve_schedule(dept_id=int(dept_id), target_dt=target_dt)
        patient = _get_or_create_patient(name=name, phone=phone, gender=gender, id_card=id_card)

        visit = Visit(
            patient_id=patient.patient_id,
            room_id=schedule.room_id,
            doctor_id=schedule.doctor_id,
            appt_id=None,
            status="候诊中",
        )
        db.session.add(visit)

        db.session.flush()
        visit_data = visit.to_dict()
        db.session.commit()
        return ok(visit_data, status=201)
    except APIError:
        db.session.rollback()
        raise
    except Exception:
        db.session.rollback()
        raise


@bp.get("/visits")
@roles_required("receptionist")
def list_visits():
    q = Visit.query.order_by(Visit.visit_id.desc())
    status = (request.args.get("status") or "").strip()
    if status:
        q = q.filter(Visit.status == status)
    visits = q.limit(100).all()
    return ok([v.to_dict() for v in visits])


@bp.get("/patients")
@roles_required("receptionist")
def list_patients():
    q = Patient.query.order_by(Patient.patient_id.desc())

    name = (request.args.get("name") or "").strip()
    phone = (request.args.get("phone") or "").strip()
    id_card = (request.args.get("id_card") or "").strip()

    if name:
        q = q.filter(Patient.name.like(f"%{name}%"))
    if phone:
        q = q.filter(Patient.phone == phone)
    if id_card:
        q = q.filter(Patient.id_card == id_card)

    patients = q.limit(200).all()
    return ok([p.to_dict() for p in patients])


_VISIT_TRANSITIONS: dict[str, set[str]] = {
    "候诊中": {"就诊中"},
    "就诊中": {"待缴费"},
    "待缴费": {"已离院"},
    "已离院": set(),
}


@bp.put("/visits/<int:visit_id>/status")
@roles_required("receptionist")
def update_visit_status(visit_id: int):
    payload = request.get_json(silent=True) or {}
    new_status = (payload.get("status") or "").strip()
    if not new_status:
        raise APIError("status is required", code="validation_error", status=400)

    visit = Visit.query.get(visit_id)
    if visit is None:
        raise APIError("Visit not found", code="not_found", status=404)

    allowed = _VISIT_TRANSITIONS.get(visit.status, set())
    if new_status not in allowed:
        raise APIError(
            "Invalid status transition",
            code="invalid_state",
            status=409,
            details={"from": visit.status, "to": new_status, "allowed": sorted(allowed)},
        )

    visit.status = new_status
    db.session.commit()
    return ok(visit.to_dict())


@bp.post("/payment/<int:visit_id>")
@roles_required("receptionist")
def pay(visit_id: int):
    payload = request.get_json(silent=True) or {}

    total = _parse_money(payload.get("total_amount"), field="total_amount")
    insurance = _parse_money(payload.get("insurance_amount", "0"), field="insurance_amount")
    self_pay_raw = payload.get("self_pay_amount")
    self_pay = (
        _parse_money(self_pay_raw, field="self_pay_amount")
        if self_pay_raw is not None
        else (total - insurance).quantize(_MONEY_CENT, rounding=ROUND_HALF_UP)
    )

    if total < 0 or insurance < 0 or self_pay < 0:
        raise APIError("Amount must be >= 0", code="validation_error", status=400)
    if insurance > total:
        raise APIError(
            "Amounts must satisfy: insurance <= total",
            code="validation_error",
            status=400,
        )
    if (insurance + self_pay) != total:
        raise APIError(
            "Amounts must satisfy: total = insurance + self_pay",
            code="validation_error",
            status=400,
        )

    try:
        visit = Visit.query.get(visit_id)
        if visit is None:
            raise APIError("Visit not found", code="not_found", status=404)
        if visit.status != "待缴费":
            raise APIError(f"Visit status is {visit.status}", code="invalid_state", status=409)

        bill = Bill.query.filter_by(visit_id=visit_id).first()
        if bill is None:
            bill = Bill(visit_id=visit_id)
            db.session.add(bill)

        bill.total_amount = total
        bill.insurance_amount = insurance
        bill.self_pay_amount = self_pay
        bill.pay_status = "已支付"
        bill.pay_time = datetime.utcnow()

        visit.status = "已离院"
        visit.checkout_time = datetime.utcnow()

        db.session.flush()  # 需要 bill_id 用于收入记录

        dept_id = visit.room.dept_id if visit.room else None
        if dept_id is None:
            raise APIError("Visit room is missing", code="invalid_state", status=409)

        record = IncomeRecord(
            bill_id=bill.bill_id,
            dept_id=dept_id,
            doctor_id=visit.doctor_id,
            amount=total,
            record_date=date.today(),
        )
        db.session.add(record)

        db.session.flush()
        visit_data = visit.to_dict()
        bill_data = bill.to_dict()
        db.session.commit()
        return ok({"visit": visit_data, "bill": bill_data})
    except APIError:
        db.session.rollback()
        raise
    except Exception:
        db.session.rollback()
        raise


@bp.get("/bills")
@roles_required("receptionist")
def list_bills():
    q = (
        Bill.query.join(Visit, Bill.visit_id == Visit.visit_id)
        .join(Patient, Visit.patient_id == Patient.patient_id)
        .join(Room, Visit.room_id == Room.room_id)
        .order_by(Bill.bill_id.desc())
    )

    pay_status = (request.args.get("pay_status") or "").strip()
    name = (request.args.get("name") or "").strip()
    phone = (request.args.get("phone") or "").strip()
    id_card = (request.args.get("id_card") or "").strip()
    room_number = (request.args.get("room_number") or "").strip()
    dept_id = (request.args.get("dept_id") or "").strip()
    doctor_id = (request.args.get("doctor_id") or "").strip()
    start_date = (request.args.get("start_date") or "").strip()
    end_date = (request.args.get("end_date") or "").strip()
    start_time = (request.args.get("start_time") or "").strip()
    end_time = (request.args.get("end_time") or "").strip()

    limit = min(_parse_int(request.args.get("limit") or "100", field="limit"), 200)
    offset = max(_parse_int(request.args.get("offset") or "0", field="offset"), 0)

    if pay_status:
        if pay_status not in ("未支付", "已支付"):
            raise APIError("Invalid pay_status", code="validation_error", status=400)
        q = q.filter(Bill.pay_status == pay_status)
    if name:
        q = q.filter(Patient.name.like(f"%{name}%"))
    if phone:
        q = q.filter(Patient.phone == phone)
    if id_card:
        q = q.filter(Patient.id_card == id_card)
    if room_number:
        q = q.filter(Room.room_number == room_number)
    if dept_id:
        q = q.filter(Room.dept_id == _parse_int(dept_id, field="dept_id"))
    if doctor_id:
        q = q.filter(Visit.doctor_id == doctor_id)

    # Prefer pay_time for paid bills; fall back to created_at filters for compatibility.
    time_field = Bill.pay_time if pay_status == "已支付" else Bill.created_at

    if start_time:
        q = q.filter(time_field >= parse_datetime(start_time))
    elif start_date:
        start = parse_date(start_date)
        q = q.filter(time_field >= datetime.combine(start, time.min))

    if end_time:
        q = q.filter(time_field <= parse_datetime(end_time))
    elif end_date:
        end = parse_date(end_date)
        q = q.filter(time_field <= datetime.combine(end, time.max))

    total = q.count()
    items = q.offset(offset).limit(limit).all()
    return ok(
        {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": [{"bill": b.to_dict(), "visit": b.visit.to_dict() if b.visit else None} for b in items],
        }
    )


@bp.get("/income-records")
@roles_required("receptionist")
def list_income_records():
    q = IncomeRecord.query.order_by(IncomeRecord.record_id.desc())

    start_date = (request.args.get("start_date") or "").strip()
    end_date = (request.args.get("end_date") or "").strip()
    dept_id = (request.args.get("dept_id") or "").strip()
    doctor_id = (request.args.get("doctor_id") or "").strip()

    limit = min(_parse_int(request.args.get("limit") or "100", field="limit"), 200)
    offset = max(_parse_int(request.args.get("offset") or "0", field="offset"), 0)

    if start_date:
        q = q.filter(IncomeRecord.record_date >= parse_date(start_date))
    if end_date:
        q = q.filter(IncomeRecord.record_date <= parse_date(end_date))
    if dept_id:
        q = q.filter(IncomeRecord.dept_id == _parse_int(dept_id, field="dept_id"))
    if doctor_id:
        q = q.filter(IncomeRecord.doctor_id == doctor_id)

    total = q.count()
    items = q.offset(offset).limit(limit).all()
    return ok({"total": total, "limit": limit, "offset": offset, "items": [r.to_dict() for r in items]})

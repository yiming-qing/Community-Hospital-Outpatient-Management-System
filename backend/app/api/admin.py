from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal

from flask import Blueprint, request
from sqlalchemy import func

from ..extensions import db
from ..models import Bill, Department, Employee, IncomeRecord, MedicalRecord, Patient, Room, Schedule, Visit
from ..utils.auth import roles_required
from ..utils.datetime_utils import parse_date, parse_datetime
from ..utils.errors import APIError
from ..utils.responses import ok

bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@bp.get("/rooms")
@roles_required("admin")
def list_rooms():
    rooms = Room.query.order_by(Room.room_id.asc()).all()
    return ok([r.to_dict() for r in rooms])


@bp.post("/rooms")
@roles_required("admin")
def create_room():
    payload = request.get_json(silent=True) or {}
    room_number = (payload.get("room_number") or "").strip()
    dept_id = payload.get("dept_id")
    status = (payload.get("status") or "启用").strip()

    if not room_number or not dept_id:
        raise APIError("room_number and dept_id are required", code="validation_error", status=400)
    if status not in ("启用", "停用"):
        raise APIError("Invalid status", code="validation_error", status=400)
    if Department.query.get(dept_id) is None:
        raise APIError("Invalid dept_id", code="validation_error", status=400)

    room = Room(room_number=room_number, dept_id=dept_id, status=status)
    db.session.add(room)
    db.session.commit()
    return ok(room.to_dict(), status=201)


@bp.put("/rooms/<int:room_id>")
@roles_required("admin")
def update_room(room_id: int):
    room = Room.query.get(room_id)
    if room is None:
        raise APIError("Room not found", code="not_found", status=404)

    payload = request.get_json(silent=True) or {}
    if "room_number" in payload:
        room.room_number = (payload.get("room_number") or "").strip()
    if "dept_id" in payload:
        dept_id = payload.get("dept_id")
        if Department.query.get(dept_id) is None:
            raise APIError("Invalid dept_id", code="validation_error", status=400)
        room.dept_id = dept_id
    if "status" in payload:
        status = (payload.get("status") or "").strip()
        if status not in ("启用", "停用"):
            raise APIError("Invalid status", code="validation_error", status=400)
        room.status = status

    db.session.commit()
    return ok(room.to_dict())


@bp.get("/schedules")
@roles_required("admin")
def list_schedules():
    q = Schedule.query.order_by(Schedule.work_date.desc(), Schedule.schedule_id.desc())
    work_date = (request.args.get("work_date") or "").strip()
    if work_date:
        q = q.filter(Schedule.work_date == parse_date(work_date))
    schedules = q.limit(200).all()
    return ok([s.to_dict() for s in schedules])


@bp.post("/schedules")
@roles_required("admin")
def create_schedule():
    payload = request.get_json(silent=True) or {}
    room_id = payload.get("room_id")
    doctor_id = (payload.get("doctor_id") or "").strip()
    work_date = parse_date(payload.get("work_date") or "")
    time_slot = (payload.get("time_slot") or "").strip()
    max_patients = payload.get("max_patients", 30)

    if not room_id or not doctor_id or not time_slot:
        raise APIError("room_id, doctor_id, work_date, time_slot are required", code="validation_error", status=400)
    if time_slot not in ("上午", "下午", "全天"):
        raise APIError("Invalid time_slot", code="validation_error", status=400)
    if Room.query.get(room_id) is None:
        raise APIError("Invalid room_id", code="validation_error", status=400)
    if Employee.query.get(doctor_id) is None:
        raise APIError("Invalid doctor_id", code="validation_error", status=400)

    schedule = Schedule(
        room_id=room_id,
        doctor_id=doctor_id,
        work_date=work_date,
        time_slot=time_slot,
        max_patients=int(max_patients),
        current_patients=0,
    )
    db.session.add(schedule)
    db.session.commit()
    return ok(schedule.to_dict(), status=201)


@bp.put("/schedules/<int:schedule_id>")
@roles_required("admin")
def update_schedule(schedule_id: int):
    schedule = Schedule.query.get(schedule_id)
    if schedule is None:
        raise APIError("Schedule not found", code="not_found", status=404)

    payload = request.get_json(silent=True) or {}
    if "room_id" in payload:
        room_id = payload.get("room_id")
        if Room.query.get(room_id) is None:
            raise APIError("Invalid room_id", code="validation_error", status=400)
        schedule.room_id = room_id
    if "doctor_id" in payload:
        doctor_id = (payload.get("doctor_id") or "").strip()
        if Employee.query.get(doctor_id) is None:
            raise APIError("Invalid doctor_id", code="validation_error", status=400)
        schedule.doctor_id = doctor_id
    if "work_date" in payload:
        schedule.work_date = parse_date(payload.get("work_date") or "")
    if "time_slot" in payload:
        time_slot = (payload.get("time_slot") or "").strip()
        if time_slot not in ("上午", "下午", "全天"):
            raise APIError("Invalid time_slot", code="validation_error", status=400)
        schedule.time_slot = time_slot
    if "max_patients" in payload:
        schedule.max_patients = int(payload.get("max_patients"))
        if schedule.current_patients > schedule.max_patients:
            raise APIError("current_patients exceeds max_patients", code="validation_error", status=400)

    db.session.commit()
    return ok(schedule.to_dict())


@bp.delete("/schedules/<int:schedule_id>")
@roles_required("admin")
def delete_schedule(schedule_id: int):
    schedule = Schedule.query.get(schedule_id)
    if schedule is None:
        raise APIError("Schedule not found", code="not_found", status=404)
    db.session.delete(schedule)
    db.session.commit()
    return ok({"deleted": True})


@bp.get("/employees")
@roles_required("admin")
def list_employees():
    employees = Employee.query.order_by(Employee.emp_id.asc()).limit(500).all()
    return ok([e.to_dict() for e in employees])


@bp.post("/employees")
@roles_required("admin")
def create_employee():
    payload = request.get_json(silent=True) or {}
    emp_id = (payload.get("emp_id") or "").strip()
    name = (payload.get("name") or "").strip()
    gender = (payload.get("gender") or "").strip()
    position = (payload.get("position") or "").strip()
    dept_id = payload.get("dept_id")
    phone = (payload.get("phone") or "").strip() or None
    title = (payload.get("title") or "").strip() or None
    status = (payload.get("status") or "在职").strip()

    if not emp_id or not name:
        raise APIError("emp_id and name are required", code="validation_error", status=400)
    if gender not in ("男", "女"):
        raise APIError("Invalid gender", code="validation_error", status=400)
    if position not in ("医生", "护士", "前台", "管理员"):
        raise APIError("Invalid position", code="validation_error", status=400)
    if status not in ("在职", "离职", "休假"):
        raise APIError("Invalid status", code="validation_error", status=400)
    if dept_id is not None and Department.query.get(dept_id) is None:
        raise APIError("Invalid dept_id", code="validation_error", status=400)

    employee = Employee(
        emp_id=emp_id,
        name=name,
        gender=gender,
        phone=phone,
        position=position,
        title=title,
        dept_id=dept_id,
        status=status,
    )
    db.session.add(employee)
    db.session.commit()
    return ok(employee.to_dict(), status=201)


@bp.put("/employees/<string:emp_id>")
@roles_required("admin")
def update_employee(emp_id: str):
    employee = Employee.query.get(emp_id)
    if employee is None:
        raise APIError("Employee not found", code="not_found", status=404)

    payload = request.get_json(silent=True) or {}
    for field in ("name", "phone", "title"):
        if field in payload:
            setattr(employee, field, (payload.get(field) or "").strip() or None)

    if "gender" in payload:
        gender = (payload.get("gender") or "").strip()
        if gender not in ("男", "女"):
            raise APIError("Invalid gender", code="validation_error", status=400)
        employee.gender = gender

    if "position" in payload:
        position = (payload.get("position") or "").strip()
        if position not in ("医生", "护士", "前台", "管理员"):
            raise APIError("Invalid position", code="validation_error", status=400)
        employee.position = position

    if "dept_id" in payload:
        dept_id = payload.get("dept_id")
        if dept_id is not None and Department.query.get(dept_id) is None:
            raise APIError("Invalid dept_id", code="validation_error", status=400)
        employee.dept_id = dept_id

    if "status" in payload:
        status = (payload.get("status") or "").strip()
        if status not in ("在职", "离职", "休假"):
            raise APIError("Invalid status", code="validation_error", status=400)
        employee.status = status

    db.session.commit()
    return ok(employee.to_dict())


@bp.get("/patients/search")
@roles_required("admin")
def search_patients():
    q = Patient.query

    name = (request.args.get("name") or "").strip()
    phone = (request.args.get("phone") or "").strip()
    id_card = (request.args.get("id_card") or "").strip()

    if name:
        q = q.filter(Patient.name.like(f"%{name}%"))
    if phone:
        q = q.filter(Patient.phone == phone)
    if id_card:
        q = q.filter(Patient.id_card == id_card)

    patients = q.order_by(Patient.patient_id.desc()).limit(100).all()
    return ok([p.to_dict() for p in patients])


def _parse_int(value: str | None, *, field: str) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except Exception as e:
        raise APIError(f"Invalid {field}", code="validation_error", status=400) from e


def _parse_decimal(value: str | None, *, field: str) -> Decimal:
    try:
        return Decimal(str(value))
    except Exception as e:
        raise APIError(f"Invalid {field}", code="validation_error", status=400) from e


@bp.get("/visits/search")
@roles_required("admin")
def search_visits():
    q = (
        Visit.query.join(Patient, Visit.patient_id == Patient.patient_id)
        .join(Room, Visit.room_id == Room.room_id)
        .order_by(Visit.visit_id.desc())
    )

    visit_id = (request.args.get("visit_id") or "").strip()
    appt_id = (request.args.get("appt_id") or "").strip()
    name = (request.args.get("name") or "").strip()
    phone = (request.args.get("phone") or "").strip()
    id_card = (request.args.get("id_card") or "").strip()
    room_number = (request.args.get("room_number") or "").strip()
    dept_id = (request.args.get("dept_id") or "").strip()
    doctor_id = (request.args.get("doctor_id") or "").strip()
    status = (request.args.get("status") or "").strip()

    start_time = (request.args.get("start_time") or "").strip()
    end_time = (request.args.get("end_time") or "").strip()
    start_date = (request.args.get("start_date") or "").strip()
    end_date = (request.args.get("end_date") or "").strip()

    limit = min(_parse_int(request.args.get("limit") or "100", field="limit"), 200)
    offset = max(_parse_int(request.args.get("offset") or "0", field="offset"), 0)

    if visit_id:
        q = q.filter(Visit.visit_id == _parse_int(visit_id, field="visit_id"))
    if appt_id:
        q = q.filter(Visit.appt_id == _parse_int(appt_id, field="appt_id"))
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
    if status:
        q = q.filter(Visit.status == status)

    if start_time:
        q = q.filter(Visit.check_in_time >= parse_datetime(start_time))
    elif start_date:
        start = parse_date(start_date)
        q = q.filter(Visit.check_in_time >= datetime.combine(start, time.min))

    if end_time:
        q = q.filter(Visit.check_in_time <= parse_datetime(end_time))
    elif end_date:
        end = parse_date(end_date)
        q = q.filter(Visit.check_in_time <= datetime.combine(end, time.max))

    total = q.count()
    items = q.offset(offset).limit(limit).all()
    return ok({"total": total, "limit": limit, "offset": offset, "items": [v.to_dict() for v in items]})


@bp.get("/visits/<int:visit_id>/medical-record")
@roles_required("admin")
def get_visit_medical_record(visit_id: int):
    if Visit.query.get(visit_id) is None:
        raise APIError("Visit not found", code="not_found", status=404)

    record = MedicalRecord.query.filter_by(visit_id=visit_id).first()
    return ok(record.to_dict() if record else None)


@bp.put("/visits/<int:visit_id>/medical-record")
@roles_required("admin")
def upsert_visit_medical_record(visit_id: int):
    if Visit.query.get(visit_id) is None:
        raise APIError("Visit not found", code="not_found", status=404)

    payload = request.get_json(silent=True) or {}
    record = MedicalRecord.query.filter_by(visit_id=visit_id).first()
    if record is None:
        record = MedicalRecord(visit_id=visit_id)
        db.session.add(record)

    for field in ("diagnosis", "treatment", "prescription", "note"):
        if field in payload:
            value = (payload.get(field) or "").strip() or None
            setattr(record, field, value)

    db.session.commit()
    return ok(record.to_dict())


@bp.get("/income-records")
@roles_required("admin")
def list_income_records():
    q = IncomeRecord.query.order_by(IncomeRecord.record_id.desc())

    start_date = (request.args.get("start_date") or "").strip()
    end_date = (request.args.get("end_date") or "").strip()
    dept_id = (request.args.get("dept_id") or "").strip()
    doctor_id = (request.args.get("doctor_id") or "").strip()
    min_amount = (request.args.get("min_amount") or "").strip()
    max_amount = (request.args.get("max_amount") or "").strip()

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
    if min_amount:
        q = q.filter(IncomeRecord.amount >= _parse_decimal(min_amount, field="min_amount"))
    if max_amount:
        q = q.filter(IncomeRecord.amount <= _parse_decimal(max_amount, field="max_amount"))

    total = q.count()
    items = q.offset(offset).limit(limit).all()
    return ok({"total": total, "limit": limit, "offset": offset, "items": [r.to_dict() for r in items]})


@bp.get("/bills")
@roles_required("admin")
def list_bills():
    q = (
        Bill.query.join(Visit, Bill.visit_id == Visit.visit_id)
        .join(Patient, Visit.patient_id == Patient.patient_id)
        .join(Room, Visit.room_id == Room.room_id)
        .order_by(Bill.bill_id.desc())
    )

    visit_id = (request.args.get("visit_id") or "").strip()
    pay_status = (request.args.get("pay_status") or "").strip()
    name = (request.args.get("name") or "").strip()
    phone = (request.args.get("phone") or "").strip()
    id_card = (request.args.get("id_card") or "").strip()
    room_number = (request.args.get("room_number") or "").strip()
    dept_id = (request.args.get("dept_id") or "").strip()
    doctor_id = (request.args.get("doctor_id") or "").strip()
    start_date = (request.args.get("start_date") or "").strip()
    end_date = (request.args.get("end_date") or "").strip()

    limit = min(_parse_int(request.args.get("limit") or "100", field="limit"), 200)
    offset = max(_parse_int(request.args.get("offset") or "0", field="offset"), 0)

    if visit_id:
        q = q.filter(Bill.visit_id == _parse_int(visit_id, field="visit_id"))
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
    if start_date:
        start = parse_date(start_date)
        q = q.filter(Bill.created_at >= datetime.combine(start, time.min))
    if end_date:
        end = parse_date(end_date)
        q = q.filter(Bill.created_at <= datetime.combine(end, time.max))

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


@bp.get("/statistics/income")
@roles_required("admin")
def stats_income():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    group_by = (request.args.get("group_by") or "dept").strip()

    start = parse_date(start_date) if start_date else date.today()
    end = parse_date(end_date) if end_date else date.today()

    q = IncomeRecord.query.filter(IncomeRecord.record_date >= start).filter(IncomeRecord.record_date <= end)

    if group_by in ("day", "date"):
        rows = (
            q.with_entities(IncomeRecord.record_date, func.sum(IncomeRecord.amount), func.count(IncomeRecord.record_id))
            .group_by(IncomeRecord.record_date)
            .order_by(IncomeRecord.record_date.asc())
            .all()
        )
        data = [{"date": d.isoformat(), "amount": float(total), "records": int(cnt)} for d, total, cnt in rows]
        return ok(
            {"group_by": "day", "start_date": start.isoformat(), "end_date": end.isoformat(), "data": data}
        )

    if group_by == "doctor":
        rows = (
            q.join(Employee, IncomeRecord.doctor_id == Employee.emp_id, isouter=True)
            .with_entities(IncomeRecord.doctor_id, Employee.name, func.sum(IncomeRecord.amount), func.count(IncomeRecord.record_id))
            .group_by(IncomeRecord.doctor_id, Employee.name)
            .all()
        )
        data = [
            {"doctor_id": did, "doctor_name": name, "amount": float(total), "records": int(cnt)}
            for did, name, total, cnt in rows
        ]
        return ok({"group_by": "doctor", "start_date": start.isoformat(), "end_date": end.isoformat(), "data": data})

    if group_by != "dept":
        raise APIError("Invalid group_by", code="validation_error", status=400)

    rows = (
        q.join(Department, IncomeRecord.dept_id == Department.dept_id)
        .with_entities(IncomeRecord.dept_id, Department.dept_name, func.sum(IncomeRecord.amount), func.count(IncomeRecord.record_id))
        .group_by(IncomeRecord.dept_id, Department.dept_name)
        .all()
    )
    data = [
        {"dept_id": dept_id, "dept_name": dept_name, "amount": float(total), "records": int(cnt)}
        for dept_id, dept_name, total, cnt in rows
    ]
    return ok({"group_by": "dept", "start_date": start.isoformat(), "end_date": end.isoformat(), "data": data})


@bp.get("/statistics/visits")
@roles_required("admin")
def stats_visits():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    group_by = (request.args.get("group_by") or "dept").strip()

    start = parse_date(start_date) if start_date else date.today()
    end = parse_date(end_date) if end_date else date.today()

    start_dt = datetime.combine(start, time.min)
    end_dt = datetime.combine(end, time.max)

    q = Visit.query.filter(Visit.check_in_time >= start_dt).filter(Visit.check_in_time <= end_dt)
    status = (request.args.get("status") or "").strip()
    if status:
        q = q.filter(Visit.status == status)

    if group_by in ("day", "date"):
        rows = (
            q.with_entities(
                func.date(Visit.check_in_time),
                func.count(Visit.visit_id),
                func.count(func.distinct(Visit.patient_id)),
            )
            .group_by(func.date(Visit.check_in_time))
            .order_by(func.date(Visit.check_in_time).asc())
            .all()
        )
        data = [{"date": str(day), "visits": int(cnt), "patients": int(pcnt)} for day, cnt, pcnt in rows]
        return ok(
            {
                "group_by": "day",
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "status": status or None,
                "data": data,
            }
        )

    if group_by == "doctor":
        rows = (
            q.join(Employee, Visit.doctor_id == Employee.emp_id, isouter=True)
            .with_entities(
                Visit.doctor_id,
                Employee.name,
                func.count(Visit.visit_id),
                func.count(func.distinct(Visit.patient_id)),
            )
            .group_by(Visit.doctor_id, Employee.name)
            .all()
        )
        data = [
            {"doctor_id": did, "doctor_name": name, "visits": int(cnt), "patients": int(pcnt)}
            for did, name, cnt, pcnt in rows
        ]
        return ok(
            {
                "group_by": "doctor",
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "status": status or None,
                "data": data,
            }
        )

    if group_by != "dept":
        raise APIError("Invalid group_by", code="validation_error", status=400)

    rows = (
        q.join(Room, Visit.room_id == Room.room_id)
        .join(Department, Room.dept_id == Department.dept_id)
        .with_entities(
            Room.dept_id,
            Department.dept_name,
            func.count(Visit.visit_id),
            func.count(func.distinct(Visit.patient_id)),
        )
        .group_by(Room.dept_id, Department.dept_name)
        .all()
    )
    data = [
        {"dept_id": dept_id, "dept_name": dept_name, "visits": int(cnt), "patients": int(pcnt)}
        for dept_id, dept_name, cnt, pcnt in rows
    ]
    return ok(
        {
            "group_by": "dept",
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "status": status or None,
            "data": data,
        }
    )

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from decimal import Decimal

from werkzeug.security import generate_password_hash

from .extensions import db
from .models import (
    Appointment,
    Bill,
    Department,
    Employee,
    IncomeRecord,
    MedicalRecord,
    Patient,
    PatientUser,
    Room,
    Schedule,
    SysUser,
    Visit,
)


def seed_demo_data() -> None:
    """
    Idempotent seed for demo: departments/rooms/employees/users/schedules + a few sample records.
    """
    departments = [
        (1, "内科", "常见内科疾病诊疗"),
        (2, "外科", "常见外科疾病诊疗"),
        (3, "口腔科", "口腔检查与治疗"),
        (4, "儿科", "儿童常见病诊疗"),
        (5, "中医科", "传统中医调理与治疗"),
        (6, "妇产科", "妇科检查与产前检查"),
        (7, "皮肤科", "各类皮肤病诊治"),
        (8, "耳鼻喉科", "耳鼻咽喉相关疾病"),
        (9, "康复医学科", "康复训练与物理治疗"),
    ]
    for dept_id, dept_name, description in departments:
        if Department.query.get(dept_id) is None:
            db.session.add(Department(dept_id=dept_id, dept_name=dept_name, description=description))

    rooms = [
        (1, "101", 1),
        (2, "102", 1),
        (3, "201", 2),
        (4, "301", 3),
        (5, "401", 4),
        (6, "501", 5),
        (7, "601", 6),
        (8, "701", 7),
        (9, "801", 8),
        (10, "901", 9),
    ]
    for room_id, room_number, dept_id in rooms:
        if Room.query.get(room_id) is None:
            db.session.add(Room(room_id=room_id, room_number=room_number, dept_id=dept_id, status="启用"))

    doctors = [
        ("D001", "李医生", "男", "13800000001", 1, "主任医师"),
        ("D002", "王医生", "女", "13800000002", 2, "副主任医师"),
        ("D003", "张医生", "男", "13800000003", 3, "主治医师"),
        ("D004", "赵医生", "女", "13800000004", 4, "主治医师"),
        ("D005", "孙医生", "男", "13800000005", 5, "主任医师"),
        ("D006", "周医生", "女", "13800000006", 6, "副主任医师"),
        ("D007", "吴医生", "男", "13800000007", 7, "主治医师"),
        ("D008", "郑医生", "男", "13800000008", 8, "主治医师"),
        ("D009", "钱医生", "女", "13800000009", 9, "主治医师"),
    ]
    for emp_id, name, gender, phone, dept_id, title in doctors:
        if Employee.query.get(emp_id) is None:
            db.session.add(
                Employee(
                    emp_id=emp_id,
                    name=name,
                    gender=gender,
                    phone=phone,
                    position="医生",
                    title=title,
                    dept_id=dept_id,
                    status="在职",
                )
            )

    staff = [
        ("R001", "前台小赵", "女", "13800000011", "前台", 1, None),
        ("A001", "管理员小陈", "男", "13800000021", "管理员", None, None),
    ]
    for emp_id, name, gender, phone, position, dept_id, title in staff:
        if Employee.query.get(emp_id) is None:
            db.session.add(
                Employee(
                    emp_id=emp_id,
                    name=name,
                    gender=gender,
                    phone=phone,
                    position=position,
                    title=title,
                    dept_id=dept_id,
                    status="在职",
                )
            )

    def upsert_user(*, username: str, role: str, emp_id: str, password: str):
        user = SysUser.query.filter_by(username=username).first()
        if user is None:
            user = SysUser(username=username, role=role, emp_id=emp_id, status="active")
            user.password_hash = generate_password_hash(password)
            db.session.add(user)

    upsert_user(username="admin", role="admin", emp_id="A001", password="admin123")
    upsert_user(username="reception", role="receptionist", emp_id="R001", password="reception123")

    test_patients = [
        (1, "张三", "男", "440101199001011234", "13911112222"),
        (2, "李四", "女", "440101199102022345", "13922223333"),
        (3, "王五", "男", "440101199203033456", "13933334444"),
    ]
    for p_id, name, gender, id_card, phone in test_patients:
        if Patient.query.get(p_id) is None:
            db.session.add(Patient(patient_id=p_id, name=name, gender=gender, id_card=id_card, phone=phone))

    db.session.commit()

    # Optional demo patient account for quick testing (patient1 / patient123)
    patient_user = SysUser.query.filter_by(username="patient1").first()
    if patient_user is None:
        patient_user = SysUser(username="patient1", role="patient", status="active")
        patient_user.password_hash = generate_password_hash("patient123")
        db.session.add(patient_user)
        db.session.flush()

    if patient_user.role == "patient":
        if PatientUser.query.filter_by(user_id=patient_user.user_id).first() is None:
            if PatientUser.query.filter_by(patient_id=1).first() is None:
                db.session.add(PatientUser(user_id=patient_user.user_id, patient_id=1))
            else:
                # if patient 1 already linked, link to the latest patient id instead
                latest = Patient.query.order_by(Patient.patient_id.desc()).first()
                if latest is not None:
                    db.session.add(PatientUser(user_id=patient_user.user_id, patient_id=latest.patient_id))

    today = date.today()

    # Schedules: ensure every department has at least one doctor+room schedule for today and tomorrow.
    dept_first_room: dict[int, int] = {}
    for room_id, _room_number, dept_id in rooms:
        dept_first_room.setdefault(dept_id, room_id)
    dept_doctor: dict[int, str] = {dept_id: emp_id for emp_id, _n, _g, _p, dept_id, _t in doctors}

    work_dates = [today + timedelta(days=i) for i in range(0, 7)]
    time_slots = ("上午", "下午")
    for dept_id, room_id in dept_first_room.items():
        doctor_id = dept_doctor.get(dept_id)
        if not doctor_id:
            continue
        for work_date in work_dates:
            for slot in time_slots:
                exists = Schedule.query.filter_by(room_id=room_id, work_date=work_date, time_slot=slot).first()
                if exists is None:
                    db.session.add(
                        Schedule(
                            room_id=room_id,
                            doctor_id=doctor_id,
                            work_date=work_date,
                            time_slot=slot,
                            max_patients=30,
                            current_patients=0,
                        )
                    )

    # Sample appointments
    if Appointment.query.count() == 0:
        db.session.add_all(
            [
                Appointment(
                    patient_name="张三",
                    phone="13911112222",
                    dept_id=1,
                    expected_time=datetime.combine(today, time(9, 30)),
                    status="待确认",
                    patient_id=1,
                ),
                Appointment(
                    patient_name="李四",
                    phone="13922223333",
                    dept_id=2,
                    expected_time=datetime.combine(today, time(10, 0)),
                    status="已确认",
                    patient_id=2,
                ),
            ]
        )

    # One completed visit + bill + income record for charts
    if Visit.query.count() == 0:
        visit = Visit(patient_id=3, room_id=dept_first_room[1], doctor_id=dept_doctor[1], appt_id=None, status="已离院")
        visit.check_in_time = datetime.now() - timedelta(hours=2)
        visit.checkout_time = datetime.now() - timedelta(hours=1)
        db.session.add(visit)
        db.session.flush()

        db.session.add(
            MedicalRecord(
                visit_id=visit.visit_id,
                diagnosis="上呼吸道感染（示例）",
                treatment="对症处理，注意休息，多喝水",
                prescription="感冒灵颗粒 * 1盒（示例）",
                note="AUTO_SEED 示例病历",
            )
        )

        bill = Bill(
            visit_id=visit.visit_id,
            total_amount=Decimal("150.00"),
            insurance_amount=Decimal("100.00"),
            self_pay_amount=Decimal("50.00"),
            pay_status="已支付",
        )
        bill.pay_time = datetime.now() - timedelta(hours=1)
        db.session.add(bill)
        db.session.flush()

        income = IncomeRecord(
            bill_id=bill.bill_id,
            dept_id=1,
            doctor_id=dept_doctor[1],
            amount=Decimal("150.00"),
            record_date=today,
        )
        db.session.add(income)

    db.session.commit()


def ensure_seed_data() -> bool:
    """
    Create tables and seed demo data (idempotent).
    Returns True if executed.
    """
    db.create_all()
    seed_demo_data()
    return True

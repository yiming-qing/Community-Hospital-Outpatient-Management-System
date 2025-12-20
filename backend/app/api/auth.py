from __future__ import annotations

from datetime import datetime

from flask import Blueprint, request
from flask_jwt_extended import create_access_token, current_user, jwt_required

from ..extensions import db
from ..models import Patient, PatientUser, SysUser
from ..utils.errors import APIError
from ..utils.responses import ok

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    if not username or not password:
        raise APIError("username and password are required", code="validation_error", status=400)

    user = SysUser.query.filter_by(username=username).first()
    if user is None or user.status != "active" or not user.check_password(password):
        raise APIError("Invalid credentials", code="invalid_credentials", status=401)

    user.last_login = datetime.utcnow()
    db.session.commit()

    token = create_access_token(identity=str(user.user_id), additional_claims={"role": user.role})
    return ok({"access_token": token, "user": user.to_safe_dict()})


@bp.post("/register")
def register_patient():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    name = (payload.get("name") or "").strip()
    phone = (payload.get("phone") or "").strip()
    gender = (payload.get("gender") or "").strip() or None
    id_card = (payload.get("id_card") or "").strip() or None

    if not username or not password:
        raise APIError("username and password are required", code="validation_error", status=400)
    if len(username) < 3:
        raise APIError("username must be at least 3 characters", code="validation_error", status=400)
    if len(password) < 6:
        raise APIError("password must be at least 6 characters", code="validation_error", status=400)
    if not name or not phone:
        raise APIError("name and phone are required", code="validation_error", status=400)
    if gender is not None and gender not in ("男", "女"):
        raise APIError("Invalid gender", code="validation_error", status=400)

    if SysUser.query.filter_by(username=username).first() is not None:
        raise APIError("username already exists", code="conflict", status=409)

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
    else:
        if id_card and not patient.id_card:
            patient.id_card = id_card
        if gender and not patient.gender:
            patient.gender = gender

    if PatientUser.query.filter_by(patient_id=patient.patient_id).first() is not None:
        raise APIError("patient already has an account", code="conflict", status=409)

    user = SysUser(username=username, role="patient", status="active")
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    link = PatientUser(user_id=user.user_id, patient_id=patient.patient_id)
    db.session.add(link)

    user.last_login = datetime.utcnow()
    db.session.commit()

    token = create_access_token(identity=str(user.user_id), additional_claims={"role": user.role})
    return ok({"access_token": token, "user": user.to_safe_dict()}, status=201)


@bp.get("/profile")
@jwt_required()
def profile():
    if current_user is None:
        raise APIError("Unauthorized", code="unauthorized", status=401)
    return ok({"user": current_user.to_safe_dict()})


@bp.post("/logout")
@jwt_required()
def logout():
    # 简化：不做 token blocklist；前端删除 token 即视为登出
    return ok({"message": "logged out"})

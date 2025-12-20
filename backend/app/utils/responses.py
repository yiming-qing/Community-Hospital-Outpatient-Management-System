from __future__ import annotations

from flask import jsonify


def ok(data=None, status: int = 200):
    return jsonify({"ok": True, "data": data}), status


def error(message: str, *, code: str = "bad_request", status: int = 400, details=None):
    payload = {"ok": False, "error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["details"] = details
    return jsonify(payload), status


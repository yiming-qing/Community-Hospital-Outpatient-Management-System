from __future__ import annotations

from datetime import date, datetime

from .errors import APIError


def parse_datetime(value: str) -> datetime:
    value = (value or "").strip()
    if not value:
        raise APIError("expected_time is required", code="validation_error", status=400)

    # 兼容：2025-12-19T09:30:00 / 2025-12-19 09:30 / 2025-12-19 09:30:00
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        pass

    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    raise APIError("Invalid datetime format", code="validation_error", status=400)


def parse_date(value: str) -> date:
    value = (value or "").strip()
    if not value:
        raise APIError("date is required", code="validation_error", status=400)
    try:
        return date.fromisoformat(value)
    except ValueError as e:
        raise APIError("Invalid date format", code="validation_error", status=400) from e


def detect_time_slot(dt: datetime) -> str:
    # 简化：12:00 前为上午，否则为下午
    return "上午" if dt.hour < 12 else "下午"

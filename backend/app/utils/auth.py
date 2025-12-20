from __future__ import annotations

from functools import wraps

from flask_jwt_extended import current_user, verify_jwt_in_request

from .errors import APIError


def roles_required(*roles: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            if current_user is None:
                raise APIError("Unauthorized", code="unauthorized", status=401)
            if current_user.status != "active":
                raise APIError("Unauthorized", code="unauthorized", status=401)
            if current_user.role not in roles:
                raise APIError("Forbidden", code="forbidden", status=403)
            return fn(*args, **kwargs)

        return wrapper

    return decorator

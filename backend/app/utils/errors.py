from __future__ import annotations

from dataclasses import dataclass

from flask import Flask

from .responses import error


@dataclass
class APIError(Exception):
    message: str
    code: str = "bad_request"
    status: int = 400
    details: dict | None = None


def register_error_handlers(app: Flask) -> None:
    # NOTE: keep APIError handler first for more specific messages.
    @app.errorhandler(APIError)
    def _api_error(err: APIError):
        from ..extensions import db

        db.session.rollback()
        return error(err.message, code=err.code, status=err.status, details=err.details)

    @app.errorhandler(Exception)
    def _unhandled(err: Exception):
        from sqlalchemy.exc import DataError, IntegrityError

        from ..extensions import db

        if isinstance(err, IntegrityError):
            db.session.rollback()
            return error("Database constraint violated", code="integrity_error", status=409)
        if isinstance(err, DataError):
            db.session.rollback()
            return error("Invalid data", code="data_error", status=400)

        app.logger.exception("Unhandled error: %s", err)
        return error("Internal server error", code="internal_error", status=500)

    @app.errorhandler(404)
    def _not_found(_err):
        return error("Not found", code="not_found", status=404)

    @app.errorhandler(405)
    def _method_not_allowed(_err):
        return error("Method not allowed", code="method_not_allowed", status=405)

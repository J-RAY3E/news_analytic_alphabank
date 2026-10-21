from __future__ import annotations

from typing import Any


class AppError(Exception):
    status_code = 500
    code = "internal_error"

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class DataNotReady(AppError):
    status_code = 503
    code = "data_not_ready"


class NotFound(AppError):
    status_code = 404
    code = "not_found"


class BadRequest(AppError):
    status_code = 400
    code = "bad_request"


class NotImplementedYet(AppError):
    status_code = 501
    code = "not_implemented"

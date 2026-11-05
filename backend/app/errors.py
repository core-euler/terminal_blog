"""Доменные ошибки. Роутеры переводят их в HTTP-ответы."""

from http import HTTPStatus


class DomainError(Exception):
    status = HTTPStatus.BAD_REQUEST
    code = "bad_request"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFound(DomainError):
    status = HTTPStatus.NOT_FOUND
    code = "not_found"


class InvalidPayload(DomainError):
    status = HTTPStatus.UNPROCESSABLE_ENTITY
    code = "invalid_payload"


class Forbidden(DomainError):
    status = HTTPStatus.FORBIDDEN
    code = "forbidden"


class Unauthorized(DomainError):
    status = HTTPStatus.UNAUTHORIZED
    code = "unauthorized"


class RateLimited(DomainError):
    status = HTTPStatus.TOO_MANY_REQUESTS
    code = "rate_limited"

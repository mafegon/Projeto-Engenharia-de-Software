class DomainError(Exception):
    status = 400
    code = "invalid_request"


class AuthenticationError(DomainError):
    status = 401
    code = "authentication_required"


class ConflictError(DomainError):
    status = 409
    code = "conflict"


class NotFoundError(DomainError):
    status = 404
    code = "not_found"


class ValidationError(DomainError):
    status = 422
    code = "validation_error"

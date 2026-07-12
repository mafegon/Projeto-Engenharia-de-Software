import json
from functools import wraps

from django.http import HttpRequest, JsonResponse

from platform_api.domain.errors import AuthenticationError, DomainError, ValidationError
from platform_api.repositories.memory import repository
from platform_api.services.auth import read_token


def payload(request: HttpRequest) -> dict:
    if request.content_type != "application/json":
        raise ValidationError("Use Content-Type application/json.")
    try:
        data = json.loads(request.body or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValidationError("JSON inválido.") from exc
    if not isinstance(data, dict):
        raise ValidationError("O corpo da requisição deve ser um objeto JSON.")
    return data


def ok(data=None, *, status=200, meta=None) -> JsonResponse:
    body = {"data": data}
    if meta is not None:
        body["meta"] = meta
    return JsonResponse(body, status=status)


def authenticated_user_id(request: HttpRequest, *, required=True) -> int | None:
    header = request.headers.get("Authorization", "")
    if not header:
        if required:
            raise AuthenticationError("Envie um token Bearer.")
        return None
    if not header.startswith("Bearer "):
        raise AuthenticationError("Envie um token Bearer.")
    user_id = read_token(header[7:].strip())
    if not repository.get_user(user_id):
        raise AuthenticationError("Usuário do token não existe.")
    return user_id


def api_view(methods, *, authenticated=False):
    allowed = frozenset(methods)

    def decorator(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if request.method not in allowed:
                response = JsonResponse(
                    {"error": {"code": "method_not_allowed", "message": "Método não permitido."}},
                    status=405,
                )
                response["Allow"] = ", ".join(sorted(allowed))
                return response
            try:
                if authenticated:
                    kwargs["user_id"] = authenticated_user_id(request)
                return view(request, *args, **kwargs)
            except DomainError as exc:
                return JsonResponse({"error": {"code": exc.code, "message": str(exc)}}, status=exc.status)
        return wrapped
    return decorator

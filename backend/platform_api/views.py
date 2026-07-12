import math

from django.http import HttpResponse

from platform_api.domain.errors import AuthenticationError, NotFoundError, ValidationError
from platform_api.http import api_view, authenticated_user_id, ok, payload
from platform_api.repositories.memory import repository
from platform_api.services.auth import login, register
from platform_api.services.platform import apply, update_profile, user_data


def _positive_int(request, name, default, maximum=None):
    raw = request.GET.get(name, default)
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{name} inválido.") from exc
    if value < 1 or (maximum is not None and value > maximum):
        raise ValidationError(f"{name} inválido.")
    return value


def _optional_user_id(request):
    return authenticated_user_id(request, required=False)


@api_view({"GET"})
def root(request):
    discovery = {
        "name": "Plataforma de Estágios Acadêmicos",
        "api_version": "v1",
        "persistence": "memory",
        "health": "/health/",
        "api_base": "/api/v1/",
    }
    if "text/html" in request.headers.get("Accept", "").lower():
        return HttpResponse(
            """<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Plataforma de Estágios Acadêmicos — Backend</title>
</head>
<body>
  <main>
    <h1>Plataforma de Estágios Acadêmicos</h1>
    <p>Backend em execução.</p>
    <dl>
      <dt>API version</dt><dd>v1</dd>
      <dt>Persistence</dt><dd>memory</dd>
    </dl>
    <nav aria-label="Recursos técnicos">
      <a href="/health/">Health: /health/</a>
      <a href="/api/v1/">API base: /api/v1/</a>
    </nav>
  </main>
</body>
</html>""",
            content_type="text/html; charset=utf-8",
        )
    return ok(discovery)


@api_view({"GET"})
def meta(request):
    return ok({"name": "Plataforma de Estágios Acadêmicos", "version": "v1", "persistence": "memory"})


@api_view({"GET"})
def courses(request):
    return ok([course.as_dict() for course in repository.list_courses()])


@api_view({"POST"})
def auth_register(request):
    user, token = register(repository, payload(request))
    return ok({"user": user, "access_token": token, "token_type": "Bearer"}, status=201)


@api_view({"POST"})
def auth_login(request):
    user, token = login(repository, payload(request))
    return ok({"user": user, "access_token": token, "token_type": "Bearer"})


@api_view({"POST"})
def password_reset(request):
    email = str(payload(request).get("email", "")).strip().lower()
    if not email.endswith("@unifap.br") or email == "@unifap.br":
        raise ValidationError("Informe um e-mail institucional @unifap.br válido.")
    return ok({"message": "Se o e-mail estiver cadastrado, as instruções serão enviadas."}, status=202)


@api_view({"GET", "PATCH"}, authenticated=True)
def profile(request, user_id):
    if request.method == "GET":
        return ok(user_data(repository, user_id))
    return ok(update_profile(repository, user_id, payload(request)))


@api_view({"GET"})
def internships(request):
    items = repository.list_internships()
    query = request.GET.get("q", "").strip().casefold()
    area = request.GET.get("area", "").strip().casefold()
    modality = request.GET.get("modality", "").strip().lower()
    weekly_hours = request.GET.get("weekly_hours", "").strip()
    saved = request.GET.get("saved", "").strip().lower()
    if modality and modality not in {"onsite", "hybrid", "remote"}:
        raise ValidationError("modality inválido.")
    if weekly_hours and weekly_hours not in {"20", "30"}:
        raise ValidationError("weekly_hours inválido.")
    if saved and saved not in {"true", "false"}:
        raise ValidationError("saved inválido.")
    user_id = _optional_user_id(request)
    if saved == "true" and user_id is None:
        raise AuthenticationError("Envie um token Bearer para filtrar vagas salvas.")
    if query:
        items = [item for item in items if query in f"{item.title} {item.company} {item.description}".casefold()]
    if area:
        items = [item for item in items if item.area.casefold() == area]
    if modality:
        items = [item for item in items if item.modality == modality]
    if weekly_hours:
        items = [item for item in items if item.weekly_hours == int(weekly_hours)]
    if saved:
        expected = saved == "true"
        items = [item for item in items if repository.is_saved(user_id, item.slug) is expected]
    page = _positive_int(request, "page", 1)
    page_size = _positive_int(request, "page_size", 20, maximum=100)
    total = len(items)
    pages = math.ceil(total / page_size)
    start = (page - 1) * page_size
    page_items = items[start:start + page_size]
    data = [item.as_dict(saved=bool(user_id and repository.is_saved(user_id, item.slug))) for item in page_items]
    return ok(data, meta={"page": page, "page_size": page_size, "total": total, "pages": pages})


@api_view({"GET"})
def internship_detail(request, slug):
    item = repository.get_internship(slug)
    if not item:
        raise NotFoundError("Vaga não encontrada.")
    user_id = _optional_user_id(request)
    return ok(item.as_dict(saved=bool(user_id and repository.is_saved(user_id, slug))))


@api_view({"PUT", "DELETE"}, authenticated=True)
def saved(request, slug, user_id):
    if not repository.get_internship(slug):
        raise NotFoundError("Vaga não encontrada.")
    if request.method == "PUT":
        repository.save_internship(user_id, slug)
        return ok({"internship_slug": slug, "saved": True})
    repository.unsave_internship(user_id, slug)
    return HttpResponse(status=204)


@api_view({"POST"}, authenticated=True)
def applications(request, slug, user_id):
    return ok(apply(repository, user_id, slug, payload(request)), status=201)

from datetime import date

from platform_api.domain.errors import ConflictError, NotFoundError, ValidationError
from platform_api.repositories.contracts import PlatformRepository


def user_data(repo: PlatformRepository, user_id: int) -> dict:
    user = repo.get_user(user_id)
    if not user:
        raise NotFoundError("Usuário não encontrado.")
    return user.public_dict(repo.get_course(user.course_code))


def update_profile(repo: PlatformRepository, user_id: int, data: dict) -> dict:
    user = repo.get_user(user_id)
    if not user:
        raise NotFoundError("Usuário não encontrado.")
    allowed = {"full_name", "phone", "city", "bio"}
    unknown = set(data) - allowed
    if unknown:
        raise ValidationError(f"Campos não permitidos: {', '.join(sorted(unknown))}.")
    if "full_name" in data and len(str(data["full_name"]).strip()) < 3:
        raise ValidationError("Informe o nome completo.")
    for field in ("phone", "city", "bio"):
        if field in data and not isinstance(data[field], str):
            raise ValidationError(f"{field} deve ser texto.")
    for key, value in data.items():
        setattr(user, key, value.strip() if isinstance(value, str) else value)
    repo.save_user(user)
    return user_data(repo, user_id)


def apply(repo: PlatformRepository, user_id: int, slug: str, data: dict) -> dict:
    if set(data) - {"cover_letter"}:
        raise ValidationError("A candidatura contém campos não permitidos.")
    item = repo.get_internship(slug)
    if not item:
        raise NotFoundError("Vaga não encontrada.")
    if item.status != "active":
        raise ValidationError("Esta vaga está encerrada.")
    if item.application_type != "internal":
        raise ValidationError("Esta vaga recebe candidaturas somente pelo link externo informado.")
    user = repo.get_user(user_id)
    if not user:
        raise NotFoundError("Usuário não encontrado.")
    if not user.phone or not user.city or not user.bio:
        raise ValidationError("Complete o perfil antes de se candidatar.")
    if user.course_code not in item.eligible_courses:
        raise ValidationError("Seu curso ou semestre não atende aos requisitos da vaga.")
    if user.semester is not None and user.semester < item.minimum_semester:
        raise ValidationError("Seu curso ou semestre não atende aos requisitos da vaga.")
    if date.today() > item.application_deadline:
        raise ValidationError("O prazo de candidatura desta vaga foi encerrado.")
    if repo.has_application(user_id, slug):
        raise ConflictError("Você já se candidatou a esta vaga.")
    cover_letter = str(data.get("cover_letter", "")).strip()
    if len(cover_letter) > 3000:
        raise ValidationError("A apresentação deve ter no máximo 3000 caracteres.")
    return repo.create_application(user_id, slug, cover_letter).as_dict()

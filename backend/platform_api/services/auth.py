import re

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core import signing
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email

from platform_api.domain.errors import AuthenticationError, ConflictError, ValidationError
from platform_api.repositories.contracts import PlatformRepository

TOKEN_SALT = "platform-api.access"
REGISTRATION_PATTERN = re.compile(r"^\d{9}$")


def issue_token(user_id: int) -> str:
    return signing.dumps({"user_id": user_id}, salt=TOKEN_SALT, compress=True)


def read_token(token: str) -> int:
    try:
        value = signing.loads(token, salt=TOKEN_SALT, max_age=int(getattr(settings, "API_TOKEN_MAX_AGE", 86400)))
        return int(value["user_id"])
    except (signing.BadSignature, KeyError, TypeError, ValueError) as exc:
        raise AuthenticationError("Token inválido ou expirado.") from exc


def register(repo: PlatformRepository, data: dict) -> tuple[dict, str]:
    required = {"full_name", "course_code", "registration", "email", "password"}
    if set(data) - required:
        raise ValidationError("O cadastro contém campos não permitidos.")
    full_name = str(data.get("full_name", "")).strip()
    course_code = str(data.get("course_code", "")).strip().lower()
    registration = str(data.get("registration", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    course = repo.get_course(course_code)
    if len(full_name.split()) < 2:
        raise ValidationError("Informe o nome completo.")
    if not course:
        raise ValidationError("Curso inválido.")
    if not REGISTRATION_PATTERN.fullmatch(registration):
        raise ValidationError("A matrícula deve conter 9 dígitos.")
    try:
        validate_email(email)
    except DjangoValidationError as exc:
        raise ValidationError("Informe um e-mail institucional @unifap.br válido.") from exc
    if email.rpartition("@")[2] != "unifap.br":
        raise ValidationError("Informe um e-mail institucional @unifap.br válido.")
    if len(password) < 8 or password.isdigit():
        raise ValidationError("A senha deve ter ao menos 8 caracteres e não pode ser apenas numérica.")
    if repo.get_user_by_email(email):
        raise ConflictError("Já existe uma conta com este e-mail.")
    if repo.get_user_by_registration(registration):
        raise ConflictError("Já existe uma conta com esta matrícula.")
    user = repo.create_user(
        full_name=full_name,
        course_code=course_code,
        registration=registration,
        email=email,
        password_hash=make_password(password),
    )
    return user.public_dict(course), issue_token(user.id)


def login(repo: PlatformRepository, data: dict) -> tuple[dict, str]:
    email = str(data.get("email", "")).strip().lower()
    user = repo.get_user_by_email(email)
    if not user or not check_password(str(data.get("password", "")), user.password_hash):
        raise AuthenticationError("E-mail ou senha inválidos.")
    return user.public_dict(repo.get_course(user.course_code)), issue_token(user.id)

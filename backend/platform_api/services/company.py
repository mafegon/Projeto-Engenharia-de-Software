import ipaddress
import re
from datetime import date, timedelta
from secrets import compare_digest
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core import signing
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import URLValidator, validate_email

from platform_api.domain.errors import AuthenticationError, ConflictError, NotFoundError, ValidationError
from platform_api.repositories.contracts import PlatformRepository

TOKEN_SALT = "platform-api.company"
MODALITIES = {"onsite", "hybrid", "remote"}
APPLICATION_TYPES = {"internal", "external"}
WEEKLY_HOURS = {20, 30}
MAX_JOBS_PER_COMPANY = 50
MAX_OPENINGS = 100
FIELD_LIMITS = {
    "legal_name": 160,
    "sector": 100,
    "phone": 30,
    "address": 240,
    "about": 3000,
    "title": 160,
    "area": 120,
    "stipend": 50,
    "location": 160,
    "description": 5000,
    "requirements": 3000,
    "external_url": 2048,
}


def issue_token(repo: PlatformRepository, company) -> str:
    return signing.dumps(
        {
            "company_id": company.id,
            "email": company.email,
            "cnpj": company.cnpj,
            "generation": repo.generation,
        },
        salt=TOKEN_SALT,
        compress=True,
    )


def read_token(token: str, repo: PlatformRepository) -> int:
    try:
        value = signing.loads(token, salt=TOKEN_SALT, max_age=int(getattr(settings, "API_TOKEN_MAX_AGE", 86400)))
        company_id = int(value["company_id"])
        generation = str(value["generation"])
        email = str(value["email"])
        cnpj = str(value["cnpj"])
    except (signing.BadSignature, KeyError, TypeError, ValueError) as exc:
        raise AuthenticationError("Token inválido ou expirado.") from exc
    company = repo.get_company(company_id)
    if (
        not company
        or not compare_digest(generation, repo.generation)
        or not compare_digest(email, company.email)
        or not compare_digest(cnpj, company.cnpj)
    ):
        raise AuthenticationError("Token inválido ou expirado.")
    return company_id


def _clean_cnpj(cnpj: str) -> str:
    return "".join(character for character in cnpj if character in "0123456789")


def _valid_cnpj(cnpj: str) -> bool:
    if not re.fullmatch(r"[0-9]{14}", cnpj, flags=re.ASCII) or len(set(cnpj)) == 1:
        return False

    def digit(prefix: str, weights: tuple[int, ...]) -> int:
        remainder = sum(int(number) * weight for number, weight in zip(prefix, weights)) % 11
        value = 11 - remainder
        return 0 if value >= 10 else value

    first = digit(cnpj[:12], (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2))
    second = digit(cnpj[:13], (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2))
    return cnpj[-2:] == f"{first}{second}"


def _limited(value: object, field: str, *, required: bool = False) -> str:
    if not isinstance(value, str):
        raise ValidationError(f"{field} deve ser texto.")
    cleaned = value.strip()
    if required and not cleaned:
        raise ValidationError(f"Informe {field}.")
    if len(cleaned) > FIELD_LIMITS[field]:
        raise ValidationError(f"{field} deve ter no máximo {FIELD_LIMITS[field]} caracteres.")
    return cleaned


def _valid_external_url(value: str) -> bool:
    try:
        URLValidator(schemes=["http", "https"])(value)
        parsed = urlsplit(value)
        if parsed.username or parsed.password or not parsed.hostname:
            return False
        hostname = parsed.hostname.casefold()
        if hostname == "localhost" or hostname.endswith(".local"):
            return False
        try:
            address = ipaddress.ip_address(hostname)
        except ValueError:
            return True
        return address.is_global
    except (DjangoValidationError, ValueError):
        return False


def register(repo: PlatformRepository, data: dict) -> tuple[dict, str]:
    required = {"legal_name", "cnpj", "sector", "email", "password"}
    if set(data) - required:
        raise ValidationError("O cadastro contém campos não permitidos.")
    legal_name = _limited(data.get("legal_name", ""), "legal_name", required=True)
    raw_cnpj = str(data.get("cnpj", "")).strip()
    cnpj = _clean_cnpj(raw_cnpj)
    sector = _limited(data.get("sector", ""), "sector", required=True)
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    if len(legal_name) < 2:
        raise ValidationError("Informe a razão social.")
    if any(character not in "0123456789.-/ " for character in raw_cnpj) or not _valid_cnpj(cnpj):
        raise ValidationError("Informe um CNPJ válido.")
    try:
        validate_email(email)
    except DjangoValidationError as exc:
        raise ValidationError("Informe um e-mail corporativo válido.") from exc
    if len(email) > 254:
        raise ValidationError("O e-mail deve ter no máximo 254 caracteres.")
    if len(password) < 8 or password.isdigit():
        raise ValidationError("A senha deve ter ao menos 8 caracteres e não pode ser apenas numérica.")
    if len(password) > 128:
        raise ValidationError("A senha deve ter no máximo 128 caracteres.")
    if repo.get_company_by_email(email):
        raise ConflictError("Já existe uma empresa com este e-mail.")
    if repo.get_company_by_cnpj(cnpj):
        raise ConflictError("Já existe uma empresa com este CNPJ.")
    formatted = f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    company = repo.create_company(
        legal_name=legal_name,
        cnpj=formatted,
        sector=sector,
        email=email,
        password_hash=make_password(password),
    )
    return company.public_dict(), issue_token(repo, company)


def login(repo: PlatformRepository, data: dict) -> tuple[dict, str]:
    email = str(data.get("email", "")).strip().lower()
    company = repo.get_company_by_email(email)
    if not company or not check_password(str(data.get("password", "")), company.password_hash):
        raise AuthenticationError("E-mail ou senha inválidos.")
    return company.public_dict(), issue_token(repo, company)


def company_data(repo: PlatformRepository, company_id: int) -> dict:
    company = repo.get_company(company_id)
    if not company:
        raise NotFoundError("Empresa não encontrada.")
    return company.public_dict()


def update_profile(repo: PlatformRepository, company_id: int, data: dict) -> dict:
    company = repo.get_company(company_id)
    if not company:
        raise NotFoundError("Empresa não encontrada.")
    allowed = {"legal_name", "sector", "phone", "address", "about"}
    unknown = set(data) - allowed
    if unknown:
        raise ValidationError(f"Campos não permitidos: {', '.join(sorted(unknown))}.")
    cleaned = {key: _limited(value, key, required=key in {"legal_name", "sector"}) for key, value in data.items()}
    if "legal_name" in cleaned and len(cleaned["legal_name"]) < 2:
        raise ValidationError("Informe a razão social.")
    for key, value in cleaned.items():
        setattr(company, key, value)
    return company_data(repo, company_id)


def _candidate_data(repo: PlatformRepository, application) -> dict | None:
    user = repo.get_user(application.user_id)
    if not user:
        return None
    course = repo.get_course(user.course_code)
    parts = user.full_name.split()
    status = "Novo" if application.status == "submitted" else application.status
    return {
        "application_id": application.id,
        "full_name": user.full_name,
        "initials": "".join(part[0] for part in parts[:2]).upper() or "AL",
        "course": course.name if course else user.course_code,
        "semester": f"{user.semester}º semestre" if user.semester is not None else "Semestre não informado",
        "applied_ago": "agora há pouco",
        "status": status,
    }


def _job_candidates(repo: PlatformRepository, job) -> list[dict]:
    candidates = (_candidate_data(repo, item) for item in repo.list_applications_for_internship(job.slug))
    return [candidate for candidate in candidates if candidate is not None]


def dashboard(repo: PlatformRepository, company_id: int) -> dict:
    company = repo.get_company(company_id)
    if not company:
        raise NotFoundError("Empresa não encontrada.")
    jobs = sorted(repo.list_company_jobs(company_id), key=lambda job: job.id)
    active = [job for job in jobs if job.status == "active"]
    job_data = []
    total_candidates = 0
    new_candidates = 0
    for job in jobs:
        candidates = _job_candidates(repo, job)
        candidate_count = len(candidates)
        new_count = sum(1 for candidate in candidates if candidate["status"] == "Novo")
        total_candidates += candidate_count
        if job.status == "active":
            new_candidates += new_count
        job_data.append(job.summary_dict(candidate_count=candidate_count, new_candidate_count=new_count))
    return {
        "company": company.public_dict(),
        "jobs": job_data,
        "stats": {
            "active_jobs": len(active),
            "total_candidates": total_candidates,
            "new_candidates": new_candidates,
        },
    }


def job_detail(repo: PlatformRepository, company_id: int, job_id: int) -> dict:
    job = repo.get_company_job(job_id)
    if not job or job.company_id != company_id:
        raise NotFoundError("Vaga não encontrada.")
    return job.as_dict(candidates=_job_candidates(repo, job))


def create_job(repo: PlatformRepository, company_id: int, data: dict) -> dict:
    if not repo.get_company(company_id):
        raise NotFoundError("Empresa não encontrada.")
    allowed = {
        "title", "area", "modality", "weekly_hours", "stipend",
        "location", "openings", "description", "requirements",
        "application_type", "external_url", "application_deadline",
    }
    unknown = set(data) - allowed
    if unknown:
        raise ValidationError(f"Campos não permitidos: {', '.join(sorted(unknown))}.")
    if len(repo.list_company_jobs(company_id)) >= MAX_JOBS_PER_COMPANY:
        raise ConflictError(f"Cada empresa pode manter no máximo {MAX_JOBS_PER_COMPANY} vagas.")
    title = _limited(data.get("title", ""), "title", required=True)
    area = _limited(data.get("area", ""), "area", required=True)
    modality = str(data.get("modality", "")).strip().lower()
    stipend = _limited(data.get("stipend", ""), "stipend", required=True)
    location = _limited(data.get("location", ""), "location", required=True)
    description = _limited(data.get("description", ""), "description", required=True)
    requirements = _limited(data.get("requirements", ""), "requirements")
    application_type = str(data.get("application_type", "internal")).strip().lower()
    external_url = _limited(data.get("external_url", ""), "external_url")
    if len(title) < 3:
        raise ValidationError("Informe o título da vaga.")
    if modality not in MODALITIES:
        raise ValidationError("Modalidade inválida.")
    if application_type not in APPLICATION_TYPES:
        raise ValidationError("Forma de candidatura inválida.")
    try:
        weekly_hours = int(data.get("weekly_hours"))
    except (TypeError, ValueError) as exc:
        raise ValidationError("Carga horária inválida.") from exc
    if weekly_hours not in WEEKLY_HOURS:
        raise ValidationError("Carga horária inválida.")
    try:
        openings = int(data.get("openings", 1))
    except (TypeError, ValueError) as exc:
        raise ValidationError("Número de vagas inválido.") from exc
    if openings < 1 or openings > MAX_OPENINGS:
        raise ValidationError("Número de vagas inválido.")
    if len(description) < 10:
        raise ValidationError("Descreva a vaga com mais detalhes.")
    if application_type == "external":
        if not _valid_external_url(external_url):
            raise ValidationError("Informe um link HTTP(S) público de candidatura externa válido.")
    else:
        external_url = ""
    deadline_value = data.get("application_deadline")
    if deadline_value in (None, ""):
        application_deadline = date.today() + timedelta(days=30)
    else:
        try:
            application_deadline = date.fromisoformat(str(deadline_value))
        except ValueError as exc:
            raise ValidationError("Prazo de candidatura inválido.") from exc
        if application_deadline < date.today():
            raise ValidationError("O prazo de candidatura não pode estar no passado.")
    job = repo.create_company_job(
        company_id,
        title=title,
        area=area,
        modality=modality,
        weekly_hours=weekly_hours,
        stipend=stipend,
        location=location,
        openings=openings,
        description=description,
        requirements=requirements,
        application_type=application_type,
        external_url=external_url,
        status="active",
        published="agora há pouco",
        application_deadline=application_deadline,
        eligible_courses=tuple(course.code for course in repo.list_courses()),
        minimum_semester=1,
    )
    return job.as_dict()


def delete_job(repo: PlatformRepository, company_id: int, job_id: int) -> None:
    job = repo.get_company_job(job_id)
    if not job or job.company_id != company_id:
        raise NotFoundError("Vaga não encontrada.")
    if repo.list_applications_for_internship(job.slug):
        raise ConflictError("A vaga possui candidaturas e não pode ser removida.")
    repo.delete_company_job(job_id)

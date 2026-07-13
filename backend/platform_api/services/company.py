import re

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core import signing
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import URLValidator, validate_email

from platform_api.domain.errors import AuthenticationError, ConflictError, NotFoundError, ValidationError
from platform_api.repositories.contracts import PlatformRepository

TOKEN_SALT = "platform-api.company"
CNPJ_PATTERN = re.compile(r"^\d{14}$")
MODALITIES = {"onsite", "hybrid", "remote"}
APPLICATION_TYPES = {"internal", "external"}
WEEKLY_HOURS = {20, 30}


def issue_token(company_id: int) -> str:
    return signing.dumps({"company_id": company_id}, salt=TOKEN_SALT, compress=True)


def read_token(token: str) -> int:
    try:
        value = signing.loads(token, salt=TOKEN_SALT, max_age=int(getattr(settings, "API_TOKEN_MAX_AGE", 86400)))
        return int(value["company_id"])
    except (signing.BadSignature, KeyError, TypeError, ValueError) as exc:
        raise AuthenticationError("Token inválido ou expirado.") from exc


def _clean_cnpj(cnpj: str) -> str:
    return "".join(filter(str.isdigit, cnpj))


def register(repo: PlatformRepository, data: dict) -> tuple[dict, str]:
    required = {"legal_name", "cnpj", "sector", "email", "password"}
    if set(data) - required:
        raise ValidationError("O cadastro contém campos não permitidos.")
    legal_name = str(data.get("legal_name", "")).strip()
    cnpj = _clean_cnpj(str(data.get("cnpj", "")))
    sector = str(data.get("sector", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    if len(legal_name) < 2:
        raise ValidationError("Informe a razão social.")
    if not CNPJ_PATTERN.fullmatch(cnpj):
        raise ValidationError("O CNPJ deve conter 14 dígitos.")
    if not sector:
        raise ValidationError("Selecione o setor da empresa.")
    try:
        validate_email(email)
    except DjangoValidationError as exc:
        raise ValidationError("Informe um e-mail corporativo válido.") from exc
    if len(password) < 8 or password.isdigit():
        raise ValidationError("A senha deve ter ao menos 8 caracteres e não pode ser apenas numérica.")
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
    return company.public_dict(), issue_token(company.id)


def login(repo: PlatformRepository, data: dict) -> tuple[dict, str]:
    email = str(data.get("email", "")).strip().lower()
    company = repo.get_company_by_email(email)
    if not company or not check_password(str(data.get("password", "")), company.password_hash):
        raise AuthenticationError("E-mail ou senha inválidos.")
    return company.public_dict(), issue_token(company.id)


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
    if "legal_name" in data and len(str(data["legal_name"]).strip()) < 2:
        raise ValidationError("Informe a razão social.")
    for field in ("sector", "phone", "address", "about"):
        if field in data and not isinstance(data[field], str):
            raise ValidationError(f"{field} deve ser texto.")
    for key, value in data.items():
        setattr(company, key, value.strip() if isinstance(value, str) else value)
    return company_data(repo, company_id)


def dashboard(repo: PlatformRepository, company_id: int) -> dict:
    company = repo.get_company(company_id)
    if not company:
        raise NotFoundError("Empresa não encontrada.")
    jobs = sorted(repo.list_company_jobs(company_id), key=lambda job: job.id)
    active = [job for job in jobs if job.status == "active"]
    return {
        "company": company.public_dict(),
        "jobs": [job.summary_dict() for job in jobs],
        "stats": {
            "active_jobs": len(active),
            "total_candidates": sum(len(job.candidates) for job in jobs),
            "new_candidates": sum(1 for job in active for candidate in job.candidates if candidate.status == "Novo"),
        },
    }


def job_detail(repo: PlatformRepository, company_id: int, job_id: int) -> dict:
    job = repo.get_company_job(job_id)
    if not job or job.company_id != company_id:
        raise NotFoundError("Vaga não encontrada.")
    return job.as_dict()


def create_job(repo: PlatformRepository, company_id: int, data: dict) -> dict:
    if not repo.get_company(company_id):
        raise NotFoundError("Empresa não encontrada.")
    allowed = {
        "title", "area", "modality", "weekly_hours", "stipend",
        "location", "openings", "description", "requirements",
        "application_type", "external_url",
    }
    unknown = set(data) - allowed
    if unknown:
        raise ValidationError(f"Campos não permitidos: {', '.join(sorted(unknown))}.")
    title = str(data.get("title", "")).strip()
    area = str(data.get("area", "")).strip()
    modality = str(data.get("modality", "")).strip().lower()
    stipend = str(data.get("stipend", "")).strip()
    location = str(data.get("location", "")).strip()
    description = str(data.get("description", "")).strip()
    requirements = str(data.get("requirements", "")).strip()
    application_type = str(data.get("application_type", "internal")).strip().lower()
    external_url = str(data.get("external_url", "")).strip()
    if len(title) < 3:
        raise ValidationError("Informe o título da vaga.")
    if not area:
        raise ValidationError("Selecione a área da vaga.")
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
    if openings < 1:
        raise ValidationError("Número de vagas inválido.")
    if not stipend:
        raise ValidationError("Informe a bolsa mensal.")
    if not location:
        raise ValidationError("Informe a localidade.")
    if len(description) < 10:
        raise ValidationError("Descreva a vaga com mais detalhes.")
    if application_type == "external":
        try:
            URLValidator()(external_url)
        except DjangoValidationError as exc:
            raise ValidationError("Informe um link de candidatura externa válido.") from exc
    else:
        external_url = ""
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
        candidates=[],
    )
    return job.as_dict()


def delete_job(repo: PlatformRepository, company_id: int, job_id: int) -> None:
    job = repo.get_company_job(job_id)
    if not job or job.company_id != company_id:
        raise NotFoundError("Vaga não encontrada.")
    repo.delete_company_job(job_id)

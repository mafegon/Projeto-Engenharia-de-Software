from datetime import date, datetime, timezone
from secrets import token_urlsafe
from threading import RLock

from platform_api.domain.entities import (
    Application,
    Company,
    CompanyJob,
    Course,
    Internship,
    User,
)


class InMemoryRepository:
    persistence = "memory"

    def __init__(self):
        self._lock = RLock()
        self.reset()

    def reset(self):
        with self._lock:
            self.generation = token_urlsafe(24)
            self.users: dict[int, User] = {
                1: User(
                    id=1,
                    full_name="Aluno Demonstração",
                    course_code="cc",
                    registration="000000001",
                    email="aluno.demo@unifap.br",
                    password_hash="!seed-user-without-login",
                    semester=5,
                    phone="(00) 00000-0000",
                    city="Cidade de demonstração",
                    bio="Perfil fictício usado somente para demonstração.",
                )
            }
            self.saved: set[tuple[int, str]] = set()
            self.applications: dict[str, Application] = {}
            self.courses = [
                Course("cc", "Ciência da Computação"),
                Course("ee", "Engenharia Elétrica"),
                Course("adm", "Administração"),
                Course("jor", "Jornalismo"),
                Course("bio", "Ciências Biológicas"),
            ]
            self.internships = [
                Internship("prodap", "PR", "Estágio em Desenvolvimento Web", "PRODAP — Centro de Gestão da TIC do Amapá", "Centro, Macapá", "Tecnologia da Informação", "hybrid", 30, "R$ 1.000/mês", "há 2 dias", "Atuação na construção e manutenção de aplicações web em Python, Django e PostgreSQL.", ("Lógica de programação e banco de dados", "Python", "HTML, CSS e Git"), ("cc",), 4, date(2026, 7, 31)),
                Internship("cea", "CE", "Estágio em Engenharia Elétrica", "CEA Equatorial", "Santa Rita, Macapá", "Engenharia", "onsite", 30, "R$ 1.100/mês", "há 3 dias", "Apoio às atividades de engenharia elétrica e manutenção.", ("Fundamentos de engenharia elétrica",), ("ee",), 3, date(2026, 8, 15)),
                Internship("tjap", "TJ", "Estágio em Comunicação Social", "Tribunal de Justiça do Amapá", "Centro, Macapá", "Comunicação", "onsite", 20, "R$ 850/mês", "há 5 dias", "Apoio à comunicação institucional e produção de conteúdo.", ("Boa comunicação escrita",), ("jor",), 3, date(2026, 8, 15)),
                Internship("basa", "BA", "Estágio em Análise de Dados", "Banco da Amazônia", "Remoto", "Tecnologia da Informação", "remote", 20, "R$ 900/mês", "há 1 semana", "Apoio à análise de dados e construção de indicadores.", ("Lógica de programação", "Planilhas"), ("cc",), 3, date(2026, 8, 31)),
                Internship("sebrae", "SE", "Estágio em Administração", "SEBRAE Amapá", "Trem, Macapá", "Administração", "onsite", 30, "R$ 800/mês", "há 1 semana", "Apoio a processos administrativos e atendimento.", ("Organização", "Comunicação"), ("adm",), 2, date(2026, 8, 31)),
                Internship("iepa", "IE", "Estágio em Meio Ambiente", "IEPA — Instituto de Pesquisas do Amapá", "Fazendinha, Macapá", "Meio Ambiente", "onsite", 20, "R$ 750/mês", "há 2 semanas", "Apoio a pesquisas e atividades de campo na área ambiental.", ("Interesse em pesquisa de campo",), ("bio",), 3, date(2026, 8, 31)),
            ]
            self.companies: dict[int, Company] = {}
            self._company_job_sequence = 0
            self.company_jobs: dict[int, CompanyJob] = {}

    def create_user(self, **values) -> User:
        with self._lock:
            user = User(id=len(self.users) + 1, **values)
            self.users[user.id] = user
            return user

    def get_user(self, user_id: int) -> User | None:
        return self.users.get(user_id)

    def save_user(self, user: User) -> User:
        with self._lock:
            self.users[user.id] = user
            return user

    def get_user_by_email(self, email: str) -> User | None:
        normalized = email.strip().lower()
        return next((user for user in self.users.values() if user.email == normalized), None)

    def get_user_by_registration(self, registration: str) -> User | None:
        return next((user for user in self.users.values() if user.registration == registration), None)

    def get_course(self, code: str) -> Course | None:
        return next((course for course in self.courses if course.code == code), None)

    def list_courses(self) -> list[Course]:
        return list(self.courses)

    def list_internships(self) -> list[Internship]:
        company_items = [self._company_job_as_internship(job) for job in self.company_jobs.values()]
        return [*self.internships, *company_items]

    def get_internship(self, slug: str) -> Internship | None:
        item = next((item for item in self.internships if item.slug == slug), None)
        if item:
            return item
        job = next((job for job in self.company_jobs.values() if job.slug == slug), None)
        return self._company_job_as_internship(job) if job else None

    def _company_job_as_internship(self, job: CompanyJob) -> Internship:
        company = self.companies[job.company_id]
        requirements = tuple(line.strip() for line in job.requirements.splitlines() if line.strip())
        return Internship(
            slug=job.slug,
            initials=company.initials,
            title=job.title,
            company=company.legal_name,
            location=job.location,
            area=job.area,
            modality=job.modality,
            weekly_hours=job.weekly_hours,
            stipend=job.stipend,
            published=job.published,
            description=job.description,
            requirements=requirements,
            eligible_courses=job.eligible_courses,
            minimum_semester=job.minimum_semester,
            application_deadline=job.application_deadline,
            application_type=job.application_type,
            external_url=job.external_url,
            status=job.status,
            company_job_id=job.id,
        )

    def save_internship(self, user_id: int, slug: str) -> None:
        with self._lock:
            self.saved.add((user_id, slug))

    def unsave_internship(self, user_id: int, slug: str) -> bool:
        with self._lock:
            key = (user_id, slug)
            existed = key in self.saved
            self.saved.discard(key)
            return existed

    def is_saved(self, user_id: int, slug: str) -> bool:
        return (user_id, slug) in self.saved

    def create_application(self, user_id: int, slug: str, cover_letter: str) -> Application:
        with self._lock:
            identifier = f"application-{len(self.applications) + 1}"
            application = Application(identifier, user_id, slug, cover_letter, submitted_at=datetime.now(timezone.utc))
            self.applications[identifier] = application
            return application

    def has_application(self, user_id: int, slug: str) -> bool:
        return any(item.user_id == user_id and item.internship_slug == slug for item in self.applications.values())

    def list_applications_for_internship(self, slug: str) -> list[Application]:
        return [item for item in self.applications.values() if item.internship_slug == slug]

    def create_company(self, **values) -> Company:
        with self._lock:
            company = Company(id=max(self.companies, default=0) + 1, **values)
            self.companies[company.id] = company
            return company

    def get_company(self, company_id: int) -> Company | None:
        return self.companies.get(company_id)

    def save_company(self, company: Company) -> Company:
        with self._lock:
            self.companies[company.id] = company
            return company

    def get_company_by_email(self, email: str) -> Company | None:
        normalized = email.strip().lower()
        return next((company for company in self.companies.values() if company.email == normalized), None)

    def get_company_by_cnpj(self, cnpj: str) -> Company | None:
        digits = "".join(character for character in cnpj if character in "0123456789")
        return next(
            (
                company for company in self.companies.values()
                if "".join(character for character in company.cnpj if character in "0123456789") == digits
            ),
            None,
        )

    def list_company_jobs(self, company_id: int) -> list[CompanyJob]:
        return [job for job in self.company_jobs.values() if job.company_id == company_id]

    def get_company_job(self, job_id: int) -> CompanyJob | None:
        return self.company_jobs.get(job_id)

    def create_company_job(self, company_id: int, **values) -> CompanyJob:
        with self._lock:
            self._company_job_sequence += 1
            job_id = self._company_job_sequence
            job = CompanyJob(id=job_id, company_id=company_id, slug=f"company-{company_id}-job-{job_id}", **values)
            self.company_jobs[job.id] = job
            return job

    def delete_company_job(self, job_id: int) -> bool:
        with self._lock:
            return self.company_jobs.pop(job_id, None) is not None


repository = InMemoryRepository()

from datetime import date
from threading import RLock

from django.contrib.auth.hashers import make_password

from platform_api.domain.entities import (
    Application,
    Company,
    CompanyJob,
    Course,
    Internship,
    JobCandidate,
    User,
)


class InMemoryRepository:
    def __init__(self):
        self._lock = RLock()
        self.reset()

    def reset(self):
        with self._lock:
            self.users: dict[int, User] = {
                1: User(
                    id=1,
                    full_name="Maria Fernanda Fernandes",
                    course_code="cc",
                    registration="202512345",
                    email="maria.fernanda@unifap.br",
                    password_hash="!seed-user-without-login",
                    semester=5,
                    phone="(96) 99123-4567",
                    city="Macapá, AP",
                    bio="Estudante de Ciência da Computação.",
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
            self.companies: dict[int, Company] = {
                1: Company(
                    id=1,
                    legal_name="PRODAP — Centro de Gestão da TIC do Amapá",
                    cnpj="34.925.222/0001-97",
                    sector="Setor público",
                    email="estagios@prodap.ap.gov.br",
                    password_hash=make_password("prodap-estagios-2026"),
                    phone="(96) 3212-1000",
                    address="Rua São José, 282 — Centro, Macapá, AP",
                    about="O PRODAP é o Centro de Gestão da Tecnologia da Informação e Comunicação do Estado do Amapá, responsável pelos sistemas e pela infraestrutura de TI do governo estadual. Oferecemos estágios em desenvolvimento, dados e infraestrutura.",
                )
            }
            self._company_job_sequence = 0
            self.company_jobs: dict[int, CompanyJob] = {}
            for values in (
                dict(title="Estágio em Desenvolvimento Web", area="Tecnologia da Informação", modality="hybrid", weekly_hours=30, stipend="R$ 1.000/mês", location="Centro, Macapá", openings=2, description="Atuação no time de desenvolvimento de sistemas web do PRODAP, participando da construção de aplicações para o governo do estado. O estagiário acompanhará o ciclo completo de desenvolvimento, do levantamento de requisitos à publicação.", requirements="Cursando a partir do 4º semestre de Ciência da Computação ou áreas afins. Conhecimentos em HTML, CSS, JavaScript e noções de banco de dados. Desejável familiaridade com Python.", application_type="internal", status="active", published="há 2 dias", candidates=[
                    JobCandidate("Maria Fernanda Fernandes", "Ciência da Computação", "5º semestre", "há 1 dia", "Novo"),
                    JobCandidate("Elton Braian", "Ciência da Computação", "6º semestre", "há 1 dia", "Novo"),
                    JobCandidate("Daniela Sepeda", "Sistemas de Informação", "4º semestre", "há 2 dias", "Em análise"),
                    JobCandidate("Geovanni Rodrigues", "Engenharia Elétrica", "7º semestre", "há 2 dias", "Em análise"),
                    JobCandidate("Vitória Ataíde", "Ciência da Computação", "5º semestre", "há 3 dias", "Visualizado"),
                ]),
                dict(title="Estágio em Análise de Dados", area="Tecnologia da Informação", modality="remote", weekly_hours=20, stipend="R$ 900/mês", location="Remoto", openings=1, description="Apoio à construção de painéis e indicadores a partir das bases de dados do governo estadual, com acompanhamento da equipe de dados.", requirements="Lógica de programação, noções de SQL e planilhas. Interesse em visualização de dados.", application_type="internal", status="active", published="há 1 semana", candidates=[
                    JobCandidate("Ana Beatriz Costa", "Ciência da Computação", "5º semestre", "há 2 dias", "Novo"),
                    JobCandidate("Rafael Nunes", "Estatística", "6º semestre", "há 4 dias", "Em análise"),
                    JobCandidate("Lucas Andrade", "Sistemas de Informação", "5º semestre", "há 5 dias", "Visualizado"),
                ]),
                dict(title="Estágio em Suporte Técnico", area="Tecnologia da Informação", modality="onsite", weekly_hours=30, stipend="R$ 800/mês", location="Centro, Macapá", openings=1, description="Atendimento de primeiro nível e apoio à equipe de infraestrutura de TI.", requirements="Conhecimentos básicos de redes e manutenção de computadores.", application_type="external", external_url="https://prodap.ap.gov.br/carreiras", status="active", published="há 2 semanas", candidates=[]),
                dict(title="Estágio em Design de Interfaces", area="Tecnologia da Informação", modality="hybrid", weekly_hours=20, stipend="R$ 850/mês", location="Centro, Macapá", openings=1, description="Apoio ao time de produto na criação de telas e protótipos dos sistemas do governo estadual.", requirements="Portfólio com projetos de UI. Domínio de Figma.", application_type="internal", status="closed", published="há 2 meses", candidates=[
                    JobCandidate("Camila Reis", "Design", "6º semestre", "há 2 meses", "Visualizado"),
                    JobCandidate("Pedro Henrique Lima", "Ciência da Computação", "7º semestre", "há 2 meses", "Em análise"),
                ]),
            ):
                self._company_job_sequence += 1
                self.company_jobs[self._company_job_sequence] = CompanyJob(id=self._company_job_sequence, company_id=1, **values)

    def create_user(self, **values) -> User:
        with self._lock:
            user = User(id=len(self.users) + 1, **values)
            self.users[user.id] = user
            return user

    def get_user(self, user_id: int) -> User | None:
        return self.users.get(user_id)

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
        return list(self.internships)

    def get_internship(self, slug: str) -> Internship | None:
        return next((item for item in self.internships if item.slug == slug), None)

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
            application = Application(identifier, user_id, slug, cover_letter)
            self.applications[identifier] = application
            return application

    def has_application(self, user_id: int, slug: str) -> bool:
        return any(item.user_id == user_id and item.internship_slug == slug for item in self.applications.values())

    def create_company(self, **values) -> Company:
        with self._lock:
            company = Company(id=max(self.companies, default=0) + 1, **values)
            self.companies[company.id] = company
            return company

    def get_company(self, company_id: int) -> Company | None:
        return self.companies.get(company_id)

    def get_company_by_email(self, email: str) -> Company | None:
        normalized = email.strip().lower()
        return next((company for company in self.companies.values() if company.email == normalized), None)

    def get_company_by_cnpj(self, cnpj: str) -> Company | None:
        digits = "".join(filter(str.isdigit, cnpj))
        return next((company for company in self.companies.values() if "".join(filter(str.isdigit, company.cnpj)) == digits), None)

    def list_company_jobs(self, company_id: int) -> list[CompanyJob]:
        return [job for job in self.company_jobs.values() if job.company_id == company_id]

    def get_company_job(self, job_id: int) -> CompanyJob | None:
        return self.company_jobs.get(job_id)

    def create_company_job(self, company_id: int, **values) -> CompanyJob:
        with self._lock:
            self._company_job_sequence += 1
            job = CompanyJob(id=self._company_job_sequence, company_id=company_id, **values)
            self.company_jobs[job.id] = job
            return job

    def delete_company_job(self, job_id: int) -> bool:
        with self._lock:
            return self.company_jobs.pop(job_id, None) is not None


repository = InMemoryRepository()

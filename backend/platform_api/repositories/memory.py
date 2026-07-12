from datetime import date
from threading import RLock

from platform_api.domain.entities import Application, Course, Internship, User


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


repository = InMemoryRepository()

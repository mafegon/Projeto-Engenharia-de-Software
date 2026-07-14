from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone


@dataclass(frozen=True, slots=True)
class Course:
    code: str
    name: str

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class User:
    id: int
    full_name: str
    course_code: str
    registration: str
    email: str
    password_hash: str
    semester: int | None = None
    phone: str = ""
    city: str = ""
    bio: str = ""

    def public_dict(self, course: Course) -> dict:
        return {
            "full_name": self.full_name,
            "email": self.email,
            "course": course.as_dict(),
            "registration": self.registration,
            "semester": self.semester,
            "phone": self.phone,
            "city": self.city,
            "bio": self.bio,
        }


@dataclass(frozen=True, slots=True)
class Internship:
    slug: str
    initials: str
    title: str
    company: str
    location: str
    area: str
    modality: str
    weekly_hours: int
    stipend: str
    published: str
    description: str
    requirements: tuple[str, ...]
    eligible_courses: tuple[str, ...]
    minimum_semester: int
    application_deadline: date
    application_type: str = "internal"
    external_url: str = ""
    status: str = "active"
    company_job_id: int | None = None

    def as_dict(self, *, saved: bool = False) -> dict:
        data = asdict(self)
        data["requirements"] = list(self.requirements)
        data["eligible_courses"] = list(self.eligible_courses)
        data["application_deadline"] = self.application_deadline.isoformat()
        data["saved"] = saved
        return data


@dataclass(frozen=True, slots=True)
class Application:
    id: str
    user_id: int
    internship_slug: str
    cover_letter: str
    status: str = "submitted"
    submitted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def as_dict(self) -> dict:
        return {"id": self.id, "internship_slug": self.internship_slug, "status": self.status}


@dataclass(slots=True)
class Company:
    id: int
    legal_name: str
    cnpj: str
    sector: str
    email: str
    password_hash: str
    phone: str = ""
    address: str = ""
    about: str = ""

    @property
    def initials(self) -> str:
        first = next((word for word in self.legal_name.split() if word[:1].isalnum()), "")
        return (first[:2] or "EM").upper()

    def public_dict(self) -> dict:
        return {
            "id": self.id,
            "legal_name": self.legal_name,
            "cnpj": self.cnpj,
            "sector": self.sector,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "about": self.about,
            "initials": self.initials,
        }


@dataclass(slots=True)
class CompanyJob:
    id: int
    company_id: int
    slug: str
    title: str
    area: str
    modality: str
    weekly_hours: int
    stipend: str
    location: str
    openings: int
    description: str
    requirements: str
    application_deadline: date
    eligible_courses: tuple[str, ...]
    minimum_semester: int
    application_type: str = "internal"
    external_url: str = ""
    status: str = "active"
    published: str = "agora há pouco"

    def summary_dict(self, *, candidate_count: int = 0, new_candidate_count: int = 0) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "area": self.area,
            "modality": self.modality,
            "weekly_hours": self.weekly_hours,
            "stipend": self.stipend,
            "location": self.location,
            "application_type": self.application_type,
            "status": self.status,
            "published": self.published,
            "candidate_count": candidate_count,
            "new_candidate_count": new_candidate_count,
        }

    def as_dict(self, *, candidates: list[dict] | None = None) -> dict:
        candidates = candidates or []
        data = self.summary_dict(
            candidate_count=len(candidates),
            new_candidate_count=sum(1 for candidate in candidates if candidate["status"] == "Novo"),
        )
        data.update(
            {
                "company_id": self.company_id,
                "slug": self.slug,
                "openings": self.openings,
                "description": self.description,
                "requirements": self.requirements,
                "external_url": self.external_url,
                "application_deadline": self.application_deadline.isoformat(),
                "eligible_courses": list(self.eligible_courses),
                "minimum_semester": self.minimum_semester,
                "candidates": candidates,
            }
        )
        return data

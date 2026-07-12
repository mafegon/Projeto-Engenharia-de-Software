from dataclasses import asdict, dataclass
from datetime import date


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

    def as_dict(self) -> dict:
        return {"id": self.id, "internship_slug": self.internship_slug, "status": self.status}

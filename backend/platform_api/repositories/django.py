from secrets import token_urlsafe

from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.utils import timezone
from django.utils.crypto import salted_hmac

from platform_api import models
from platform_api.domain.entities import Application, Company, CompanyJob, Course, Internship, User
from platform_api.domain.errors import ConflictError


def _digits(value: str) -> str:
    return "".join(character for character in value if character.isdigit())


class DjangoRepository:
    persistence = "django"

    @property
    def generation(self) -> str:
        explicit = getattr(settings, "PLATFORM_TOKEN_GENERATION", "")
        return explicit or salted_hmac("platform-api.generation", settings.SECRET_KEY).hexdigest()

    @staticmethod
    def _course(row):
        return Course(row.code, row.name)

    @staticmethod
    def _user(row):
        return User(row.pk, row.full_name, row.course_id, row.registration, row.account.email, row.account.password_hash,
                    row.semester, row.phone or "", row.city or "", row.bio or "")

    @staticmethod
    def _company(row):
        return Company(row.pk, row.legal_name, row.cnpj, row.trade_name, row.account.email, row.account.password_hash,
                       row.phone or "", row.address or "", row.about or "")

    @staticmethod
    def _internship(row):
        requirements = row.requirements if isinstance(row.requirements, list) else []
        return Internship(
            row.slug, DjangoRepository._company(row.company).initials, row.title, row.company.legal_name,
            row.location, row.area, row.modality, row.weekly_hours, row.stipend or "", "agora há pouco",
            row.description, tuple(map(str, requirements)),
            tuple(row.eligible_courses.values_list("code", flat=True)), row.minimum_semester,
            row.application_deadline, "external" if row.external_application else "internal",
            row.external_url, "active" if row.status in {"ativa", "active"} else "closed", row.pk,
        )

    @staticmethod
    def _company_job(row):
        requirements = row.requirements if isinstance(row.requirements, list) else []
        return CompanyJob(
            row.pk, row.company_id, row.slug, row.title, row.area, row.modality, row.weekly_hours,
            row.stipend or "", row.location, row.openings, row.description, "\n".join(map(str, requirements)),
            row.application_deadline, tuple(row.eligible_courses.values_list("code", flat=True)),
            row.minimum_semester, "external" if row.external_application else "internal",
            row.external_url, "active" if row.status in {"ativa", "active"} else "closed", "agora há pouco",
        )

    @staticmethod
    def _application(row):
        return Application(str(row.pk), row.student_id, row.internship.slug, row.cover_letter or "",
                           row.status, row.submitted_at)

    def create_user(self, **values):
        try:
            with transaction.atomic():
                account = models.Account.objects.create(
                    email=values["email"].strip().lower(), password_hash=values["password_hash"]
                )
                row = models.Student.objects.create(
                    account=account, full_name=values["full_name"], course_id=values["course_code"],
                    registration=values["registration"], semester=values.get("semester"),
                    phone=values.get("phone", ""), city=values.get("city", ""), bio=values.get("bio", ""),
                )
        except IntegrityError as exc:
            raise ConflictError("Já existe uma conta com este e-mail ou matrícula.") from exc
        return self._user(row)

    def save_user(self, user):
        try:
            with transaction.atomic():
                row = models.Student.objects.select_related("account").get(pk=user.id)
                models.Account.objects.filter(pk=row.account_id).update(
                    email=user.email.strip().lower(), password_hash=user.password_hash
                )
                models.Student.objects.filter(pk=user.id).update(
                    full_name=user.full_name, course_id=user.course_code, registration=user.registration,
                    semester=user.semester, phone=user.phone, city=user.city, bio=user.bio,
                    updated_at=timezone.now(),
                )
        except IntegrityError as exc:
            raise ConflictError("Já existe uma conta com este e-mail ou matrícula.") from exc
        return self.get_user(user.id) or user

    def get_user(self, user_id):
        row = models.Student.objects.select_related("course", "account").filter(pk=user_id).first()
        return self._user(row) if row else None

    def get_user_by_email(self, email):
        row = models.Student.objects.select_related("course", "account").filter(
            account__email__iexact=email.strip()).first()
        return self._user(row) if row else None

    def get_user_by_registration(self, registration):
        row = models.Student.objects.select_related("course", "account").filter(registration=registration).first()
        return self._user(row) if row else None

    def get_course(self, code):
        row = models.Course.objects.filter(pk=code).first()
        return self._course(row) if row else None

    def list_courses(self):
        return [self._course(row) for row in models.Course.objects.all()]

    def list_internships(self):
        rows = models.Internship.objects.select_related("company__account").prefetch_related("eligible_courses")
        return [self._internship(row) for row in rows]

    def get_internship(self, slug):
        row = (models.Internship.objects.select_related("company__account").prefetch_related("eligible_courses")
               .filter(slug=slug).first())
        return self._internship(row) if row else None

    def save_internship(self, user_id, slug):
        with transaction.atomic():
            models.SavedInternship.objects.update_or_create(
                student_id=user_id, internship_id=self._internship_id(slug), defaults={"saved": True})

    def unsave_internship(self, user_id, slug):
        return bool(models.SavedInternship.objects.filter(
            student_id=user_id, internship__slug=slug, saved=True).update(saved=False))

    def is_saved(self, user_id, slug):
        return bool(user_id) and models.SavedInternship.objects.filter(
            student_id=user_id, internship__slug=slug, saved=True).exists()

    @staticmethod
    def _internship_id(slug):
        return models.Internship.objects.only("id").get(slug=slug).pk

    def create_application(self, user_id, slug, cover_letter):
        try:
            with transaction.atomic():
                row = models.Application.objects.create(
                    student_id=user_id, internship_id=self._internship_id(slug), cover_letter=cover_letter)
        except IntegrityError as exc:
            raise ConflictError("Você já se candidatou a esta vaga.") from exc
        return self._application(models.Application.objects.select_related("internship").get(pk=row.pk))

    def has_application(self, user_id, slug):
        return models.Application.objects.filter(student_id=user_id, internship__slug=slug).exists()

    def list_applications_for_internship(self, slug):
        rows = models.Application.objects.select_related("internship").filter(internship__slug=slug)
        return [self._application(row) for row in rows]

    def create_company(self, **values):
        try:
            with transaction.atomic():
                account = models.Account.objects.create(
                    email=values["email"].strip().lower(), password_hash=values["password_hash"]
                )
                row = models.Company.objects.create(
                    account=account, legal_name=values["legal_name"], cnpj=values["cnpj"],
                    trade_name=values["sector"],
                    phone=values.get("phone", ""), address=values.get("address", ""), about=values.get("about", ""),
                )
        except IntegrityError as exc:
            raise ConflictError("Já existe uma empresa com este e-mail ou CNPJ.") from exc
        return self._company(row)

    def save_company(self, company):
        try:
            with transaction.atomic():
                row = models.Company.objects.select_related("account").get(pk=company.id)
                models.Account.objects.filter(pk=row.account_id).update(
                    email=company.email.strip().lower(), password_hash=company.password_hash
                )
                models.Company.objects.filter(pk=company.id).update(
                    legal_name=company.legal_name, cnpj=company.cnpj, trade_name=company.sector,
                    phone=company.phone, address=company.address, about=company.about,
                    updated_at=timezone.now(),
                )
        except IntegrityError as exc:
            raise ConflictError("Já existe uma empresa com este e-mail ou CNPJ.") from exc
        return self.get_company(company.id) or company

    def get_company(self, company_id):
        row = models.Company.objects.select_related("account").filter(pk=company_id).first()
        return self._company(row) if row else None

    def get_company_by_email(self, email):
        row = models.Company.objects.select_related("account").filter(
            account__email__iexact=email.strip()).first()
        return self._company(row) if row else None

    def get_company_by_cnpj(self, cnpj):
        digits = _digits(cnpj)
        formatted = f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"
        row = models.Company.objects.select_related("account").filter(
            Q(cnpj=digits) | Q(cnpj=formatted)).first()
        return self._company(row) if row else None

    def list_company_jobs(self, company_id):
        rows = (models.Internship.objects.filter(company_id=company_id)
                .prefetch_related("eligible_courses").order_by("id"))
        return [self._company_job(row) for row in rows]

    def get_company_job(self, job_id):
        row = (models.Internship.objects.filter(pk=job_id, company__isnull=False)
               .prefetch_related("eligible_courses").first())
        return self._company_job(row) if row else None

    def create_company_job(self, company_id, **values):
        requirements = [line.strip() for line in values["requirements"].splitlines() if line.strip()]
        course_codes = tuple(values["eligible_courses"])
        with transaction.atomic():
            row = models.Internship.objects.create(
                company_id=company_id, slug=f"pending-{token_urlsafe(12)}",
                title=values["title"], area=values["area"],
                modality=values["modality"], weekly_hours=values["weekly_hours"],
                stipend=values["stipend"], location=values["location"], openings=values["openings"],
                description=values["description"], requirements=requirements,
                application_deadline=values["application_deadline"], minimum_semester=values["minimum_semester"],
                external_application=values.get("application_type", "internal") == "external",
                external_url=values.get("external_url", ""),
                status="ativa" if values.get("status", "active") == "active" else "encerrada",
            )
            row.slug = f"company-{company_id}-job-{row.pk}"
            row.save(update_fields=("slug",))
            row.eligible_courses.set(models.Course.objects.filter(code__in=course_codes))
        return self._company_job(models.Internship.objects.prefetch_related("eligible_courses").get(pk=row.pk))

    def delete_company_job(self, job_id):
        try:
            with transaction.atomic():
                deleted, _ = models.Internship.objects.filter(pk=job_id, company__isnull=False).delete()
        except ProtectedError as exc:
            raise ConflictError("A vaga possui candidaturas e não pode ser removida.") from exc
        return bool(deleted)


repository = DjangoRepository()

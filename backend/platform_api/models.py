from django.core.validators import MaxLengthValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import Length
from django.db.models.functions import Lower, Now
from django.db.models.lookups import LessThanOrEqual


class TextArrayField(models.JSONField):
    """PostgreSQL text[] compatible field with a JSON-backed SQLite test fallback."""

    def db_type(self, connection):
        if connection.vendor == "postgresql":
            return "text[]"
        return super().db_type(connection)

    def get_db_prep_value(self, value, connection, prepared=False):
        if connection.vendor == "postgresql":
            return list(value or [])
        return super().get_db_prep_value(value, connection, prepared)

    def from_db_value(self, value, expression, connection):
        if connection.vendor == "postgresql" and isinstance(value, list):
            return value
        return super().from_db_value(value, expression, connection)


class Course(models.Model):
    code = models.CharField(max_length=10, primary_key=True, db_column="codigo")
    name = models.CharField(max_length=100, db_column="nome")

    class Meta:
        db_table = "cursos"
        ordering = ("name",)


class Account(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=255, unique=True)
    password_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())

    class Meta:
        db_table = "usuarios"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(email=Lower("email")),
                name="usuarios_email_check",
            )
        ]


class Student(models.Model):
    id = models.AutoField(primary_key=True)
    account = models.OneToOneField(Account, db_column="usuario_id", on_delete=models.CASCADE, related_name="student")
    full_name = models.CharField(max_length=255, db_column="nome_completo")
    course = models.ForeignKey(Course, db_column="curso_codigo", on_delete=models.PROTECT, related_name="students")
    registration = models.CharField(max_length=9, unique=True, db_column="matricula")
    semester = models.IntegerField(null=True, blank=True, db_column="semestre")
    phone = models.CharField(max_length=20, blank=True, null=True, db_column="telefone")
    city = models.CharField(max_length=100, blank=True, null=True, db_column="cidade")
    bio = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, db_default=Now())

    class Meta:
        db_table = "alunos"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(registration__regex=r"^[0-9]{9}$"),
                name="alunos_matricula_check",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(semester__isnull=True)
                    | models.Q(semester__gte=1, semester__lte=20)
                ),
                name="alunos_semestre_check",
            ),
        ]


class Company(models.Model):
    id = models.AutoField(primary_key=True)
    account = models.OneToOneField(Account, db_column="usuario_id", on_delete=models.CASCADE, related_name="company")
    legal_name = models.CharField(max_length=255, db_column="razao_social")
    trade_name = models.CharField(max_length=255, blank=True, db_column="nome_fantasia")
    cnpj = models.CharField(max_length=18, unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True, db_column="telefone_contato")
    address = models.CharField(max_length=255, blank=True, null=True, db_column="endereco")
    about = models.TextField(blank=True, null=True, db_column="descricao_institucional")
    updated_at = models.DateTimeField(auto_now=True, db_default=Now())

    class Meta:
        db_table = "empresas"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    cnpj__regex=r"^(?:[0-9]{14}|[0-9]{2}\.[0-9]{3}\.[0-9]{3}/[0-9]{4}-[0-9]{2})$"
                ),
                name="empresas_cnpj_check",
            )
        ]


class Internship(models.Model):
    MODALITIES = (("onsite", "Presencial"), ("hybrid", "Híbrido"), ("remote", "Remoto"))
    APPLICATION_TYPES = (("internal", "Interna"), ("external", "Externa"))
    STATUSES = (("ativa", "Ativa"), ("encerrada", "Encerrada"), ("inativa", "Inativa"))

    id = models.AutoField(primary_key=True)
    slug = models.SlugField(max_length=80, unique=True)
    company = models.ForeignKey(
        Company, db_column="empresa_id", on_delete=models.PROTECT, related_name="jobs"
    )
    title = models.CharField(max_length=255, db_column="titulo")
    location = models.CharField(max_length=100, db_column="localidade")
    area = models.CharField(max_length=100)
    modality = models.CharField(max_length=20, choices=MODALITIES, db_column="modalidade")
    weekly_hours = models.IntegerField(
        validators=(MinValueValidator(4), MaxValueValidator(44))
    )
    stipend = models.CharField(max_length=50, blank=True, null=True)
    openings = models.IntegerField(
        default=1,
        db_column="quantidade_vagas",
        validators=(MinValueValidator(1), MaxValueValidator(100)),
    )
    description = models.TextField(db_column="descricao")
    requirements = TextArrayField(default=list, blank=True, db_column="requisitos")
    eligible_courses = models.ManyToManyField(
        Course, related_name="internships", through="InternshipCourse"
    )
    minimum_semester = models.IntegerField(
        default=1,
        validators=(MinValueValidator(1), MaxValueValidator(19)),
    )
    application_deadline = models.DateField()
    external_application = models.BooleanField(default=False, db_column="candidatura_externa")
    external_url = models.TextField(
        blank=True,
        null=True,
        db_column="link_candidatura_externa",
    )
    status = models.CharField(max_length=20, choices=STATUSES, default="ativa")
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())
    updated_at = models.DateTimeField(auto_now=True, db_default=Now())

    class Meta:
        db_table = "vagas"
        ordering = ("id",)
        constraints = [
            models.CheckConstraint(
                condition=models.Q(openings__gte=1, openings__lte=100),
                name="quantidade_vagas_entre_1_e_100",
            ),
            models.CheckConstraint(
                condition=models.Q(weekly_hours__gte=4, weekly_hours__lte=44),
                name="vagas_weekly_hours_check",
            ),
            models.CheckConstraint(
                condition=models.Q(minimum_semester__gte=1, minimum_semester__lte=19),
                name="vagas_minimum_semester_check",
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=("ativa", "encerrada", "inativa")),
                name="vagas_status_check",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(external_application=False)
                    | models.Q(external_url__isnull=False)
                ),
                name="vagas_check",
            ),
        ]


class InternshipCourse(models.Model):
    pk = models.CompositePrimaryKey("internship_id", "course_id")
    internship = models.ForeignKey(Internship, db_column="vaga_id", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, db_column="curso_codigo", on_delete=models.PROTECT)

    class Meta:
        db_table = "vaga_cursos"
        constraints = []


class SavedInternship(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, db_column="aluno_id", on_delete=models.CASCADE, related_name="saved_internships")
    internship = models.ForeignKey(Internship, db_column="vaga_id", on_delete=models.PROTECT, related_name="saved_by")
    saved = models.BooleanField(default=False, db_column="favorita")
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column="data_salvamento",
        db_default=Now(),
    )
    note = models.TextField(null=True, blank=True, db_column="observacao")

    class Meta:
        db_table = "favoritos"
        constraints = [
            models.UniqueConstraint(
                fields=("student", "internship"),
                name="favoritos_aluno_id_vaga_id_key",
            )
        ]


class Application(models.Model):
    STATUSES = (
        ("submitted", "Enviada"),
        ("under_review", "Em análise"),
        ("accepted", "Aceita"),
        ("rejected", "Rejeitada"),
    )

    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, db_column="aluno_id", on_delete=models.CASCADE, related_name="applications")
    internship = models.ForeignKey(Internship, db_column="vaga_id", on_delete=models.PROTECT, related_name="applications")
    cover_letter = models.TextField(
        null=True,
        blank=True,
        validators=(MaxLengthValidator(3000),),
    )
    status = models.CharField(max_length=20, choices=STATUSES, default="submitted")
    submitted_at = models.DateTimeField(
        auto_now_add=True,
        db_column="data_candidatura",
        db_default=Now(),
    )

    class Meta:
        db_table = "candidaturas"
        ordering = ("submitted_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("student", "internship"),
                name="candidaturas_aluno_id_vaga_id_key",
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=("submitted", "under_review", "accepted", "rejected")),
                name="candidaturas_status_check",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(cover_letter__isnull=True)
                    | models.Q(LessThanOrEqual(Length("cover_letter"), 3000))
                ),
                name="candidaturas_cover_letter_check",
            ),
        ]

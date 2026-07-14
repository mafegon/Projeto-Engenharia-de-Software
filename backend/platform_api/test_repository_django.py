from datetime import date, timedelta
from importlib import import_module
from unittest.mock import patch

from django.apps import apps
from django.db import IntegrityError, transaction
from django.db.models import CASCADE, PROTECT, AutoField, IntegerField, TextField
from django.test import TestCase, override_settings
from django.utils import timezone

from platform_api import models
from platform_api.domain.errors import ConflictError
from platform_api.repositories.django import DjangoRepository


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class DjangoRepositoryTests(TestCase):
    def setUp(self):
        self.repo = DjangoRepository()

    def test_seed_catalog_is_available(self):
        self.assertEqual(len(self.repo.list_courses()), 5)
        self.assertEqual(len(self.repo.list_internships()), 6)
        self.assertEqual(self.repo.get_internship("prodap").eligible_courses, ("cc",))

    def test_student_profile_update_is_persisted(self):
        user = self.repo.create_user(
            full_name="Estudante Teste", course_code="cc", registration="202612345",
            email="estudante@unifap.br", password_hash="hash",
        )
        user.phone = "(96) 99999-9999"
        self.repo.save_user(user)
        self.assertEqual(self.repo.get_user(user.id).phone, "(96) 99999-9999")
        with self.assertRaises(ConflictError):
            self.repo.create_user(
                full_name="Outra Pessoa", course_code="cc", registration="202612346",
                email="estudante@unifap.br", password_hash="hash",
            )

    def test_company_job_saved_application_and_deletion_protection(self):
        company = self.repo.create_company(
            legal_name="Empresa Teste Ltda", cnpj="04.252.011/0001-10", sector="Tecnologia",
            email="rh@empresa.test", password_hash="hash",
        )
        company.about = "Perfil persistido"
        self.repo.save_company(company)
        self.assertEqual(self.repo.get_company(company.id).about, "Perfil persistido")
        job = self.repo.create_company_job(
            company.id, title="Estágio em Backend", area="Tecnologia da Informação",
            modality="hybrid", weekly_hours=30, stipend="R$ 1.000/mês", location="Macapá",
            openings=7, description="Desenvolvimento e testes de APIs Django.",
            requirements="Python\nDjango", application_deadline=date.today() + timedelta(days=30),
            eligible_courses=("cc",), minimum_semester=1,
        )
        self.assertEqual(self.repo.get_company_job(job.id).openings, 7)
        student = self.repo.create_user(
            full_name="Pessoa Candidata", course_code="cc", registration="202612347",
            email="candidata@unifap.br", password_hash="hash", semester=3,
            phone="9999-9999", city="Macapá", bio="Estudante de computação",
        )
        self.repo.save_internship(student.id, job.slug)
        self.repo.save_internship(student.id, job.slug)
        self.assertTrue(self.repo.is_saved(student.id, job.slug))
        self.repo.create_application(student.id, job.slug, "Tenho interesse.")
        with self.assertRaises(ConflictError):
            self.repo.create_application(student.id, job.slug, "Duplicada")
        with self.assertRaises(ConflictError):
            self.repo.delete_company_job(job.id)

    def test_token_generation_is_persisted(self):
        generation = self.repo.generation
        self.assertEqual(generation, DjangoRepository().generation)

    def test_remote_schema_contract_is_reflected_in_model_state(self):
        for model in (
            models.Account,
            models.Student,
            models.Company,
            models.Internship,
            models.SavedInternship,
            models.Application,
        ):
            self.assertIsInstance(model._meta.pk, AutoField)
        for model, field_name in (
            (models.Student, "semester"),
            (models.Internship, "weekly_hours"),
            (models.Internship, "minimum_semester"),
            (models.Internship, "openings"),
        ):
            self.assertIsInstance(model._meta.get_field(field_name), IntegerField)
        self.assertIsInstance(models.Internship._meta.get_field("external_url"), TextField)
        self.assertTrue(models.Internship._meta.get_field("stipend").null)
        self.assertEqual(models.InternshipCourse._meta.get_field("course").remote_field.on_delete, PROTECT)
        self.assertEqual(models.SavedInternship._meta.get_field("internship").remote_field.on_delete, PROTECT)
        self.assertEqual(models.Application._meta.get_field("student").remote_field.on_delete, CASCADE)
        expected_constraints = {
            "usuarios_email_check",
            "alunos_matricula_check",
            "alunos_semestre_check",
            "empresas_cnpj_check",
            "vagas_weekly_hours_check",
            "vagas_minimum_semester_check",
            "vagas_status_check",
            "vagas_check",
            "candidaturas_status_check",
            "candidaturas_cover_letter_check",
            "favoritos_aluno_id_vaga_id_key",
            "candidaturas_aluno_id_vaga_id_key",
        }
        actual_constraints = {
            constraint.name
            for model in apps.get_app_config("platform_api").get_models()
            for constraint in model._meta.constraints
        }
        self.assertTrue(expected_constraints.issubset(actual_constraints))

    def test_nullable_remote_profile_fields_preserve_api_string_contract(self):
        account = models.Account.objects.create(email="nullable@unifap.br", password_hash="hash")
        student = models.Student.objects.create(
            account=account,
            full_name="Perfil Nulo",
            course_id="cc",
            registration="202612348",
            phone=None,
            city=None,
            bio=None,
        )
        user = self.repo.get_user(student.pk)
        self.assertEqual((user.phone, user.city, user.bio), ("", "", ""))

    def test_seed_is_idempotent(self):
        seed_catalog = import_module("platform_api.migrations.0002_seed_catalog").seed_catalog
        before = (
            models.Course.objects.count(),
            models.Account.objects.count(),
            models.Company.objects.count(),
            models.Internship.objects.count(),
            models.InternshipCourse.objects.count(),
        )
        seed_catalog(apps, None)
        seed_catalog(apps, None)
        after = (
            models.Course.objects.count(),
            models.Account.objects.count(),
            models.Company.objects.count(),
            models.Internship.objects.count(),
            models.InternshipCourse.objects.count(),
        )
        self.assertEqual(after, before)

    def test_profile_save_advances_remote_updated_timestamp(self):
        user = self.repo.create_user(
            full_name="Atualização Teste",
            course_code="cc",
            registration="202612349",
            email="atualizacao@unifap.br",
            password_hash="hash",
        )
        before = models.Student.objects.get(pk=user.id).updated_at
        instant = timezone.now() + timedelta(seconds=10)
        user.city = "Macapá"
        with patch("platform_api.repositories.django.timezone.now", return_value=instant):
            self.repo.save_user(user)
        self.assertEqual(models.Student.objects.get(pk=user.id).updated_at, instant)

    def test_database_rejects_invalid_remote_status_and_long_cover_letter(self):
        user = self.repo.create_user(
            full_name="Constraint Teste",
            course_code="cc",
            registration="202612350",
            email="constraint@unifap.br",
            password_hash="hash",
        )
        internship = models.Internship.objects.get(slug="prodap")
        with self.assertRaises(IntegrityError), transaction.atomic():
            models.Application.objects.create(
                student_id=user.id,
                internship=internship,
                status="invalid",
            )
        with self.assertRaises(IntegrityError), transaction.atomic():
            models.Application.objects.create(
                student_id=user.id,
                internship=internship,
                cover_letter="x" * 3001,
            )

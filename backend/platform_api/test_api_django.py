import json
from unittest import skipUnless

from django.conf import settings
from django.test import Client, TestCase, override_settings


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
@skipUnless(settings.PLATFORM_REPOSITORY == "django", "requer PLATFORM_REPOSITORY=django")
class DjangoPersistenceApiTests(TestCase):
    def setUp(self):
        self.client = Client(HTTP_HOST="localhost")

    def post(self, path, data, token=None):
        headers = {"HTTP_AUTHORIZATION": f"Bearer {token}"} if token else {}
        return self.client.post(path, data=json.dumps(data), content_type="application/json", **headers)

    def test_student_company_job_and_application_persist_through_api(self):
        student = self.post("/api/v1/auth/register/", {
            "full_name": "Teste Persistência", "course_code": "cc", "registration": "202699999",
            "email": "persistencia@unifap.br", "password": "senha-forte-123",
        })
        self.assertEqual(student.status_code, 201)
        student_token = student.json()["data"]["access_token"]
        profile = self.client.patch(
            "/api/v1/me/profile/",
            data=json.dumps({"phone": "(96) 99999-9999", "city": "Macapá", "bio": "Perfil local."}),
            content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {student_token}",
        )
        self.assertEqual(profile.status_code, 200)
        company = self.post("/api/v1/company/auth/register/", {
            "legal_name": "Empresa Persistência Ltda", "cnpj": "04.252.011/0001-10",
            "sector": "Tecnologia", "email": "persistencia@empresa.com.br", "password": "senha-forte-123",
        })
        self.assertEqual(company.status_code, 201)
        company_token = company.json()["data"]["access_token"]
        job = self.post("/api/v1/company/jobs/", {
            "title": "Estágio local em Backend", "area": "Tecnologia da Informação",
            "modality": "hybrid", "weekly_hours": 30, "stipend": "R$ 1.000/mês",
            "location": "Macapá", "openings": 5,
            "description": "Desenvolvimento e testes de APIs Django.",
            "requirements": "Python\nDjango", "application_type": "internal",
        }, company_token)
        self.assertEqual(job.status_code, 201)
        self.assertEqual(job.json()["data"]["openings"], 5)
        application = self.post(
            f"/api/v1/internships/{job.json()['data']['slug']}/applications/",
            {"cover_letter": "Tenho interesse."}, student_token,
        )
        self.assertEqual(application.status_code, 201)

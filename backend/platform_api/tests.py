import json

from django.conf import settings
from django.test import Client, SimpleTestCase

from platform_api.repositories.memory import repository


class PlatformApiTests(SimpleTestCase):
    def setUp(self):
        repository.reset()

    @staticmethod
    def json(response):
        return json.loads(response.content)

    def register(self, **overrides):
        data = {
            "full_name": "Geovanni Silva",
            "course_code": "cc",
            "registration": "202612345",
            "email": "geovanni@unifap.br",
            "password": "senha-forte-123",
        }
        data.update(overrides)
        return self.client.post("/api/v1/auth/register/", data=json.dumps(data), content_type="application/json")

    def token(self, **overrides):
        return self.json(self.register(**overrides))["data"]["access_token"]

    @staticmethod
    def authorization(token):
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def complete_profile(self, token, **overrides):
        data = {"phone": "(96) 99123-4567", "city": "Macapá, AP", "bio": "Estudante de computação."}
        data.update(overrides)
        return self.client.patch(
            "/api/v1/me/profile/", data=json.dumps(data), content_type="application/json", **self.authorization(token)
        )

    def test_public_metadata_and_six_screen_courses_and_internships(self):
        self.assertEqual(self.client.get("/health/").status_code, 200)
        self.assertEqual(self.json(self.client.get("/api/v1/meta/"))["data"]["persistence"], "memory")
        courses = self.json(self.client.get("/api/v1/courses/"))["data"]
        response = self.client.get("/api/v1/internships/")
        body = self.json(response)
        self.assertEqual([course["code"] for course in courses], ["cc", "ee", "adm", "jor", "bio"])
        self.assertEqual([item["slug"] for item in body["data"]], ["prodap", "cea", "tjap", "basa", "sebrae", "iepa"])
        self.assertEqual(body["meta"], {"page": 1, "page_size": 20, "total": 6, "pages": 1})

    def test_root_identifies_the_backend_and_discovery_paths(self):
        response = self.client.get("/api/v1/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("django.middleware.clickjacking.XFrameOptionsMiddleware", settings.MIDDLEWARE)
        self.assertNotIn("X-Frame-Options", response)
        self.assertEqual(
            self.json(response)["data"],
            {
                "name": "Plataforma de Estágios Acadêmicos",
                "api_version": "v1",
                "persistence": "memory",
                "health": "/health/",
                "api_base": "/api/v1/",
            },
        )

    def test_root_serves_minimal_technical_html_when_requested(self):
        response = self.client.get("/backend-status/", HTTP_ACCEPT="text/html,application/xhtml+xml")
        body = response.content.decode()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("text/html"))
        self.assertIn("Plataforma de Estágios Acadêmicos", body)
        self.assertIn("Backend em execução", body)
        self.assertIn("v1", body)
        self.assertIn("memory", body)
        self.assertIn('href="/health/"', body)
        self.assertIn('href="/api/v1/"', body)

    def test_register_enforces_institutional_contract_and_hides_password(self):
        response = self.register()
        body = self.json(response)["data"]
        self.assertEqual(response.status_code, 201)
        self.assertEqual(body["user"]["course"], {"code": "cc", "name": "Ciência da Computação"})
        self.assertEqual(body["user"]["registration"], "202612345")
        self.assertIsNone(body["user"]["semester"])
        self.assertNotIn("password_hash", body["user"])
        for overrides in (
            {"email": "aluno@example.com"},
            {"registration": "123"},
            {"password": "12345678"},
            {"course_code": "unknown"},
            {"semester": 5},
        ):
            repository.reset()
            self.assertEqual(self.register(**overrides).status_code, 422)

    def test_register_rejects_duplicate_email_and_registration(self):
        self.assertEqual(self.register().status_code, 201)
        self.assertEqual(self.register(registration="202612346").status_code, 409)
        self.assertEqual(self.register(email="outro@unifap.br").status_code, 409)

    def test_login_and_generic_password_reset(self):
        self.register()
        valid = self.client.post(
            "/api/v1/auth/login/",
            data=json.dumps({"email": "geovanni@unifap.br", "password": "senha-forte-123"}),
            content_type="application/json",
        )
        invalid = self.client.post(
            "/api/v1/auth/login/",
            data=json.dumps({"email": "geovanni@unifap.br", "password": "errada"}),
            content_type="application/json",
        )
        reset = self.client.post(
            "/api/v1/auth/password-reset/", data=json.dumps({"email": "desconhecido@unifap.br"}), content_type="application/json"
        )
        self.assertEqual(valid.status_code, 200)
        self.assertEqual(invalid.status_code, 401)
        self.assertEqual(reset.status_code, 202)

    def test_same_origin_web_ui_csrf_and_bearer_flow(self):
        browser = Client(enforce_csrf_checks=True)
        page = browser.get("/")
        csrf_token = page.cookies["csrftoken"].value
        csrf = {"HTTP_X_CSRFTOKEN": csrf_token}
        registration = {
            "full_name": "Geovanni Silva",
            "course_code": "cc",
            "registration": "202612345",
            "email": "geovanni@unifap.br",
            "password": "senha-forte-123",
        }

        blocked = browser.post(
            "/api/v1/auth/register/",
            data=json.dumps(registration),
            content_type="application/json",
        )
        self.assertEqual(blocked.status_code, 403)

        registered = browser.post(
            "/api/v1/auth/register/",
            data=json.dumps(registration),
            content_type="application/json",
            **csrf,
        )
        self.assertEqual(registered.status_code, 201)

        logged_in = browser.post(
            "/api/v1/auth/login/",
            data=json.dumps({"email": registration["email"], "password": registration["password"]}),
            content_type="application/json",
            **csrf,
        )
        self.assertEqual(logged_in.status_code, 200)
        token = self.json(logged_in)["data"]["access_token"]
        authorized = {**csrf, **self.authorization(token)}

        profile = browser.patch(
            "/api/v1/me/profile/",
            data=json.dumps(
                {
                    "phone": "(96) 99123-4567",
                    "city": "Macapá, AP",
                    "bio": "Estudante de computação.",
                }
            ),
            content_type="application/json",
            **authorized,
        )
        saved = browser.put("/api/v1/internships/prodap/saved/", **authorized)
        application = browser.post(
            "/api/v1/internships/prodap/applications/",
            data=json.dumps({"cover_letter": "Tenho interesse."}),
            content_type="application/json",
            **authorized,
        )

        self.assertEqual(profile.status_code, 200)
        self.assertEqual(saved.status_code, 200)
        self.assertEqual(application.status_code, 201)

    def test_profile_contract_and_immutable_institutional_fields(self):
        token = self.token()
        self.assertEqual(self.client.get("/api/v1/me/profile/").status_code, 401)
        updated = self.complete_profile(token)
        self.assertEqual(updated.status_code, 200)
        self.assertIsNone(self.json(updated)["data"]["semester"])
        immutable = self.client.patch(
            "/api/v1/me/profile/",
            data=json.dumps({"registration": "999999999"}),
            content_type="application/json",
            **self.authorization(token),
        )
        self.assertEqual(immutable.status_code, 422)
        semester = self.client.patch(
            "/api/v1/me/profile/",
            data=json.dumps({"semester": 5}),
            content_type="application/json",
            **self.authorization(token),
        )
        self.assertEqual(semester.status_code, 422)

    def test_internship_filters_pagination_detail_and_validation(self):
        filtered = self.client.get("/api/v1/internships/?q=dados&area=Tecnologia%20da%20Informa%C3%A7%C3%A3o&modality=remote&weekly_hours=20")
        paged = self.client.get("/api/v1/internships/?page=2&page_size=2")
        detail = self.client.get("/api/v1/internships/prodap/")
        self.assertEqual([item["slug"] for item in self.json(filtered)["data"]], ["basa"])
        self.assertEqual([item["slug"] for item in self.json(paged)["data"]], ["tjap", "basa"])
        self.assertEqual(self.json(paged)["meta"]["pages"], 3)
        self.assertEqual(self.json(detail)["data"]["weekly_hours"], 30)
        self.assertEqual(self.client.get("/api/v1/internships/unknown/").status_code, 404)
        self.assertEqual(self.client.get("/api/v1/internships/?modality=virtual").status_code, 422)
        self.assertEqual(self.client.get("/api/v1/internships/?page_size=101").status_code, 422)

    def test_saved_contract_is_idempotent_and_filter_requires_authentication(self):
        token = self.token()
        auth = self.authorization(token)
        self.assertEqual(self.client.get("/api/v1/internships/?saved=true").status_code, 401)
        self.assertEqual(self.client.put("/api/v1/internships/prodap/saved/", **auth).status_code, 200)
        self.assertEqual(self.client.put("/api/v1/internships/prodap/saved/", **auth).status_code, 200)
        filtered = self.client.get("/api/v1/internships/?saved=true", **auth)
        self.assertEqual([item["slug"] for item in self.json(filtered)["data"]], ["prodap"])
        self.assertEqual(self.client.delete("/api/v1/internships/prodap/saved/", **auth).status_code, 204)

    def test_application_requires_complete_eligible_profile_and_is_unique(self):
        token = self.token()
        auth = self.authorization(token)
        path = "/api/v1/internships/prodap/applications/"
        incomplete = self.client.post(path, data="{}", content_type="application/json", **auth)
        self.assertEqual(incomplete.status_code, 422)
        self.complete_profile(token)
        created = self.client.post(path, data=json.dumps({"cover_letter": "Tenho interesse."}), content_type="application/json", **auth)
        duplicate = self.client.post(path, data="{}", content_type="application/json", **auth)
        self.assertEqual(created.status_code, 201)
        self.assertIsNone(repository.get_user(2).semester)
        self.assertEqual(self.json(created)["data"]["internship_slug"], "prodap")
        self.assertEqual(duplicate.status_code, 409)

    def test_application_rejects_ineligible_course_or_semester(self):
        token = self.token(course_code="adm")
        self.complete_profile(token)
        response = self.client.post(
            "/api/v1/internships/prodap/applications/", data="{}", content_type="application/json", **self.authorization(token)
        )
        self.assertEqual(response.status_code, 422)

        repository.reset()
        token = self.token()
        self.complete_profile(token)
        repository.get_user(2).semester = 3
        response = self.client.post(
            "/api/v1/internships/prodap/applications/", data="{}", content_type="application/json", **self.authorization(token)
        )
        self.assertEqual(response.status_code, 422)

    def test_seed_maria_keeps_known_semester_five(self):
        maria = repository.get_user(1)
        self.assertEqual(maria.full_name, "Maria Fernanda Fernandes")
        self.assertEqual(maria.semester, 5)

    def test_http_errors_are_uniform_and_methods_publish_allow_header(self):
        invalid_json = self.client.post("/api/v1/auth/register/", data="{", content_type="application/json")
        wrong_type = self.client.post("/api/v1/auth/register/", data="{}", content_type="text/plain")
        invalid_token = self.client.get("/api/v1/me/profile/", HTTP_AUTHORIZATION="Bearer adulterado")
        wrong_method = self.client.post("/api/v1/courses/", data="{}", content_type="application/json")
        self.assertEqual(invalid_json.status_code, 422)
        self.assertEqual(wrong_type.status_code, 422)
        self.assertEqual(invalid_token.status_code, 401)
        self.assertEqual(wrong_method.status_code, 405)
        self.assertEqual(wrong_method["Allow"], "GET")
        for response in (invalid_json, wrong_type, invalid_token, wrong_method):
            self.assertEqual(set(self.json(response)["error"]), {"code", "message"})

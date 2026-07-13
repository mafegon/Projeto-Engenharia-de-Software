from django.templatetags.static import static
from django.test import SimpleTestCase, override_settings
from django.urls import resolve, reverse


class WebUiRouteTests(SimpleTestCase):
    @override_settings(DEBUG=False)
    def test_app_pages_use_manifest_versioned_api_script_in_production(self):
        script_url = static("web_ui/api.js")
        self.assertRegex(script_url, r"^/static/web_ui/api\.[0-9a-f]{12}\.js$")

        pages = (
            "/aluno/",
            "/vagas/",
            "/vagas/prodap/",
            "/perfil/",
            "/empresa/",
            "/empresa/vagas/",
            "/empresa/vagas/nova/",
            "/empresa/vagas/1/",
            "/empresa/perfil/",
        )
        for path in pages:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertContains(response, f'<script src="{script_url}"></script>')

    def test_landing_page_is_the_entrypoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Conectando alunos e empresas")
        self.assertContains(response, 'href="/aluno/"')
        self.assertContains(response, 'href="/empresa/"')
        self.assertEqual(reverse("web_ui:landing"), "/")

    def test_public_student_login_and_registration_page(self):
        response = self.client.get("/aluno/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bem-vindo(a), aluno(a)")
        self.assertContains(response, 'id="painel-entrar"')
        self.assertContains(response, 'id="painel-cadastro"')
        self.assertIn("csrftoken", response.cookies)

    def test_internship_list_page_preserves_frontend_structure(self):
        response = self.client.get("/vagas/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Vagas de estágio")
        self.assertContains(response, 'id="filtros"')
        self.assertContains(response, 'id="lista-vagas"')

    def test_internship_detail_receives_slug(self):
        response = self.client.get("/vagas/prodap/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-internship-slug="prodap"')
        self.assertContains(response, "Candidatar-se")
        self.assertEqual(resolve("/vagas/prodap/").kwargs, {"slug": "prodap"})

    def test_student_profile_page_and_named_routes(self):
        response = self.client.get("/perfil/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Meu perfil")
        self.assertContains(response, 'id="form-perfil"')
        self.assertEqual(reverse("web_ui:login"), "/aluno/")
        self.assertEqual(reverse("web_ui:internships"), "/vagas/")
        self.assertEqual(reverse("web_ui:profile"), "/perfil/")

    def test_company_login_and_registration_page(self):
        response = self.client.get("/empresa/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Área da empresa")
        self.assertContains(response, 'id="painel-entrar"')
        self.assertContains(response, 'id="painel-cadastro"')
        self.assertIn("csrftoken", response.cookies)

    def test_company_dashboard_and_named_routes(self):
        response = self.client.get("/empresa/vagas/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Minhas vagas")
        self.assertContains(response, 'id="lista-vagas"')
        self.assertEqual(reverse("web_ui:company-login"), "/empresa/")
        self.assertEqual(reverse("web_ui:company-jobs"), "/empresa/vagas/")
        self.assertEqual(reverse("web_ui:company-job-new"), "/empresa/vagas/nova/")
        self.assertEqual(reverse("web_ui:company-profile"), "/empresa/perfil/")

    def test_company_job_form_and_detail_pages(self):
        new_job = self.client.get("/empresa/vagas/nova/")
        self.assertContains(new_job, "Cadastrar vaga")
        self.assertContains(new_job, 'id="form-vaga"')

        detail = self.client.get("/empresa/vagas/3/")
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, 'data-job-id="3"')
        self.assertEqual(resolve("/empresa/vagas/3/").kwargs, {"job_id": 3})

    def test_company_profile_page(self):
        response = self.client.get("/empresa/perfil/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Perfil da empresa")
        self.assertContains(response, 'id="form-perfil"')

    def test_backend_status_was_moved_out_of_home(self):
        response = self.client.get("/backend-status/", HTTP_ACCEPT="text/html")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Backend em execução")
        self.assertNotContains(self.client.get("/"), "Backend em execução")

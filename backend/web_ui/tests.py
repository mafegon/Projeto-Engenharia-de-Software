from pathlib import Path

from django.contrib.staticfiles import finders
from django.templatetags.static import static
from django.test import SimpleTestCase, override_settings
from django.urls import resolve, reverse


class WebUiRouteTests(SimpleTestCase):
    @override_settings(DEBUG=False)
    def test_pages_use_manifest_versioned_api_script_in_production(self):
        script_url = static("web_ui/api.js")
        self.assertRegex(script_url, r"^/static/web_ui/api\.[0-9a-f]{12}\.js$")

        for path in ("/", "/vagas/", "/vagas/prodap/", "/perfil/"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertContains(response, f'<script src="{script_url}"></script>')

    def test_public_login_and_registration_page(self):
        response = self.client.get("/")
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

    def test_profile_page_and_named_routes(self):
        response = self.client.get("/perfil/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Meu perfil")
        self.assertContains(response, 'id="form-perfil"')
        self.assertEqual(reverse("web_ui:login"), "/")
        self.assertEqual(reverse("web_ui:internships"), "/vagas/")
        self.assertEqual(reverse("web_ui:profile"), "/perfil/")

    def test_authenticated_pages_start_with_neutral_profile_avatar(self):
        for path in ("/vagas/", "/vagas/prodap/", "/perfil/"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertNotContains(response, "Maria Fernanda Fernandes")
                self.assertNotContains(response, ">MF<")
                self.assertContains(response, 'aria-label="Meu perfil"')
                self.assertContains(response, "data-user-initials")
                self.assertContains(response, 'aria-hidden="true"')
                self.assertContains(response, "animate-pulse")

    def test_profile_stays_busy_and_read_only_until_hydrated(self):
        response = self.client.get("/perfil/")
        self.assertContains(response, 'id="form-perfil" aria-busy="true"')
        self.assertContains(response, 'id="perfil-status" role="status" aria-live="polite"')
        self.assertContains(response, 'id="perfil-submit" type="submit" disabled')
        self.assertContains(response, '<option value="" selected>Carregando…</option>', html=True)
        for field_id in ("perfil-nome", "perfil-telefone", "perfil-cidade", "perfil-bio"):
            self.assertContains(response, f'id="{field_id}"')
        self.assertContains(response, "disabled data-profile-editable", count=4)
        self.assertContains(response, "document.getElementById('perfil-curso').value = data.course.name")
        self.assertContains(response, "document.getElementById('perfil-submit').disabled = false")
        self.assertContains(response, "setAttribute('aria-busy', 'false')")

    def test_initials_helper_has_no_fictitious_fallback(self):
        script_path = finders.find("web_ui/api.js")
        self.assertIsNotNone(script_path)
        source = Path(script_path).read_text(encoding="utf-8")
        self.assertNotIn('String(name || "Aluno")', source)
        self.assertIn('if (!normalized) return "";', source)

    def test_backend_status_was_moved_out_of_home(self):
        response = self.client.get("/backend-status/", HTTP_ACCEPT="text/html")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Backend em execução")
        self.assertNotContains(self.client.get("/"), "Backend em execução")

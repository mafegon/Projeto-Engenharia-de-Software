from django.test import SimpleTestCase
from django.urls import resolve, reverse


class WebUiRouteTests(SimpleTestCase):
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

    def test_backend_status_was_moved_out_of_home(self):
        response = self.client.get("/backend-status/", HTTP_ACCEPT="text/html")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Backend em execução")
        self.assertNotContains(self.client.get("/"), "Backend em execução")

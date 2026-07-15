import re
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles import finders
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

    def test_landing_only_keeps_access_links_in_the_main_ctas(self):
        response = self.client.get("/")
        source = response.content.decode()

        self.assertNotIn("<nav", source)
        self.assertNotIn("Sou aluno", source)
        self.assertNotIn("Sou empresa", source)
        self.assertNotIn("<footer", source)
        self.assertNotIn("Acesso do aluno", source)
        self.assertNotIn("Acesso da empresa", source)

        student_cta = re.search(
            r'<a href="/aluno/" class="([^"]+)">Entrar como aluno</a>',
            source,
        )
        company_cta = re.search(
            r'<a href="/empresa/" class="([^"]+)">Entrar como empresa</a>',
            source,
        )
        self.assertIsNotNone(student_cta)
        self.assertIsNotNone(company_cta)
        self.assertEqual(student_cta.group(1), company_cta.group(1))

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

    def test_internship_list_starts_with_neutral_count(self):
        response = self.client.get("/vagas/")
        self.assertContains(response, 'id="resultado-contagem"')
        self.assertContains(response, "Buscando vagas…")
        self.assertNotContains(response, "6 vagas encontradas")

    def test_internship_detail_receives_slug(self):
        response = self.client.get("/vagas/prodap/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-internship-slug="prodap"')
        self.assertContains(response, "Candidatar-se")
        self.assertEqual(resolve("/vagas/prodap/").kwargs, {"slug": "prodap"})

    def test_internship_detail_starts_neutral_and_busy(self):
        response = self.client.get("/vagas/prodap/")

        self.assertNotContains(response, "PRODAP")
        self.assertNotContains(response, ">PR<")
        self.assertNotContains(response, "Estágio em Desenvolvimento Web")
        self.assertContains(response, 'id="vaga-detalhes" aria-busy="true"')
        self.assertContains(response, 'id="vaga-status" role="status" aria-live="polite"')
        self.assertContains(response, "Carregando detalhes da vaga…")
        self.assertContains(response, 'data-vaga-skeleton aria-hidden="true"')
        self.assertContains(response, 'id="btn-candidatar" onclick="candidatar()" disabled')
        self.assertContains(response, 'id="btn-salvar" onclick="alternarSalvar()" disabled')

    def test_internship_detail_hydrates_and_handles_errors_inline(self):
        source = self.client.get("/vagas/prodap/").content.decode()

        self.assertIn("if (!vaga) return;", source)
        self.assertIn("document.getElementById('btn-candidatar').disabled = false", source)
        self.assertIn("document.getElementById('btn-salvar').disabled = false", source)
        self.assertIn("setAttribute('aria-busy', 'false')", source)
        self.assertIn("error.status === 401", source)
        self.assertIn("error.status === 404", source)
        self.assertIn("Vaga não encontrada.", source)
        self.assertIn("Não foi possível carregar a vaga. Tente novamente mais tarde.", source)
        self.assertNotIn("alert(error.message)", source)

    def test_student_profile_page_and_named_routes(self):
        response = self.client.get("/perfil/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Meu perfil")
        self.assertContains(response, 'id="form-perfil"')
        self.assertEqual(reverse("web_ui:login"), "/aluno/")
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

    def test_button_cursor_rules_cover_enabled_and_disabled_states(self):
        source = (Path(settings.BASE_DIR) / "theme/static_src/src/styles.css").read_text(encoding="utf-8")
        self.assertIn("button:not(:disabled):not(.cursor-default)", source)
        self.assertIn("cursor: pointer;", source)
        self.assertIn("button:disabled:not(.cursor-default)", source)
        self.assertIn("cursor: not-allowed;", source)

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

    def test_company_pages_start_neutral_busy_and_render_api_data_safely(self):
        authenticated_pages = (
            "/empresa/vagas/",
            "/empresa/vagas/nova/",
            "/empresa/vagas/3/",
            "/empresa/perfil/",
        )
        for path in authenticated_pages:
            with self.subTest(path=path):
                source = self.client.get(path).content.decode()
                self.assertNotIn(">PR<", source)
                self.assertIn("data-company-initials", source)
                self.assertIn("aria-busy=\"true\"", source)
                self.assertNotIn("innerHTML", source)
                self.assertNotIn("alert(error.message)", source)
                self.assertIn("encodeURIComponent(window.location.pathname + window.location.search)", source)

    def test_company_loading_failures_clear_stale_loading_ui(self):
        jobs = self.client.get("/empresa/vagas/").content.decode()
        detail = self.client.get("/empresa/vagas/3/").content.decode()
        new_job = self.client.get("/empresa/vagas/nova/").content.decode()

        self.assertIn("Não foi possível carregar o resumo das vagas.", jobs)
        self.assertIn("querySelectorAll('[data-company-initials]')", jobs)
        self.assertIn("Vaga não encontrada", detail)
        self.assertIn("Detalhes indisponíveis", detail)
        self.assertIn("querySelectorAll('[data-company-initials]')", detail)
        self.assertIn("Não foi possível preparar o formulário.", new_job)
        self.assertIn("querySelectorAll('[data-company-initials]')", new_job)

    def test_large_login_images_are_desktop_only_and_deprioritized(self):
        for path, image_stem in (("/aluno/", "alunos"), ("/empresa/", "empresa")):
            with self.subTest(path=path):
                source = self.client.get(path).content.decode()
                self.assertIn('<source media="(min-width: 768px)"', source)
                self.assertIn(f"/static/web_ui/{image_stem}.", source)
                self.assertIn(".jpg", source)
                self.assertIn('src="data:image/gif;base64,', source)
                self.assertIn('loading="lazy" decoding="async" fetchpriority="low"', source)

    def test_company_initials_helper_has_no_fictitious_fallback(self):
        script_path = finders.find("web_ui/api.js")
        self.assertIsNotNone(script_path)
        source = Path(script_path).read_text(encoding="utf-8")
        self.assertNotIn('String(name || "Empresa")', source)
        self.assertIn('const first = String(name || "")', source)

    def test_login_next_redirects_are_same_origin_and_area_scoped(self):
        student = self.client.get("/aluno/").content.decode()
        company = self.client.get("/empresa/").content.decode()
        script_path = finders.find("web_ui/api.js")
        source = Path(script_path).read_text(encoding="utf-8")

        self.assertIn("Platform.safeNextPath(next)", student)
        self.assertIn("Company.safeNextPath(next)", company)
        self.assertIn('candidate.includes("\\\\")', source)
        self.assertIn('candidate.startsWith("//")', source)
        self.assertIn("url.origin !== window.location.origin", source)
        self.assertIn("/^\\/(?:aluno", source)
        self.assertIn("/^\\/empresa", source)

    def test_api_client_handles_empty_non_json_and_network_failures(self):
        script_path = finders.find("web_ui/api.js")
        source = Path(script_path).read_text(encoding="utf-8")

        self.assertIn("response = await fetch", source)
        self.assertIn("const text = await response.text()", source)
        self.assertIn("text.trim() ? JSON.parse(text) : null", source)
        self.assertNotIn("await response.json()", source)
        self.assertIn("Verifique sua conexão e tente novamente.", source)
        self.assertIn("error.status = response.status", source)

    def test_backend_status_was_moved_out_of_home(self):
        response = self.client.get("/backend-status/", HTTP_ACCEPT="text/html")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Backend em execução")
        self.assertNotContains(self.client.get("/"), "Backend em execução")

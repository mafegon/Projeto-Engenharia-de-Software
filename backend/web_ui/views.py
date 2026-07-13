from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie


def landing(request):
    return render(request, "web_ui/landing.html")


@ensure_csrf_cookie
def login(request):
    return render(request, "web_ui/login.html")


@ensure_csrf_cookie
def internships(request):
    return render(request, "web_ui/vagas.html")


@ensure_csrf_cookie
def internship_detail(request, slug):
    return render(request, "web_ui/vaga-detalhes.html", {"internship_slug": slug})


@ensure_csrf_cookie
def profile(request):
    return render(request, "web_ui/perfil.html")


@ensure_csrf_cookie
def company_login(request):
    return render(request, "web_ui/empresa/login.html")


@ensure_csrf_cookie
def company_jobs(request):
    return render(request, "web_ui/empresa/vagas.html")


@ensure_csrf_cookie
def company_job_new(request):
    return render(request, "web_ui/empresa/cadastrar-vaga.html")


@ensure_csrf_cookie
def company_job_detail(request, job_id):
    return render(request, "web_ui/empresa/vaga-detalhes.html", {"job_id": job_id})


@ensure_csrf_cookie
def company_profile(request):
    return render(request, "web_ui/empresa/perfil.html")

from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie


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


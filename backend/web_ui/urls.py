from django.urls import path

from web_ui import views

app_name = "web_ui"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("aluno/", views.login, name="login"),
    path("vagas/", views.internships, name="internships"),
    path("vagas/<slug:slug>/", views.internship_detail, name="internship-detail"),
    path("perfil/", views.profile, name="profile"),
    path("empresa/", views.company_login, name="company-login"),
    path("empresa/vagas/", views.company_jobs, name="company-jobs"),
    path("empresa/vagas/nova/", views.company_job_new, name="company-job-new"),
    path("empresa/vagas/<int:job_id>/", views.company_job_detail, name="company-job-detail"),
    path("empresa/perfil/", views.company_profile, name="company-profile"),
]

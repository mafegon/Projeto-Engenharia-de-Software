from django.urls import path

from platform_api import views

app_name = "platform_api"

urlpatterns = [
    path("", views.root, name="root"),
    path("meta/", views.meta, name="meta"),
    path("courses/", views.courses, name="courses"),
    path("auth/register/", views.auth_register, name="register"),
    path("auth/login/", views.auth_login, name="login"),
    path("auth/password-reset/", views.password_reset, name="password-reset"),
    path("me/profile/", views.profile, name="profile"),
    path("internships/", views.internships, name="internships"),
    path("internships/<slug:slug>/", views.internship_detail, name="internship-detail"),
    path("internships/<slug:slug>/saved/", views.saved, name="saved"),
    path("internships/<slug:slug>/applications/", views.applications, name="applications"),
    path("company/auth/register/", views.company_register, name="company-register"),
    path("company/auth/login/", views.company_login, name="company-login"),
    path("company/profile/", views.company_profile, name="company-profile"),
    path("company/jobs/", views.company_jobs, name="company-jobs"),
    path("company/jobs/<int:job_id>/", views.company_job_detail, name="company-job-detail"),
]

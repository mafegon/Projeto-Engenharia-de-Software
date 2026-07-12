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
]

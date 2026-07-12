from django.urls import path

from web_ui import views

app_name = "web_ui"

urlpatterns = [
    path("", views.login, name="login"),
    path("vagas/", views.internships, name="internships"),
    path("vagas/<slug:slug>/", views.internship_detail, name="internship-detail"),
    path("perfil/", views.profile, name="profile"),
]


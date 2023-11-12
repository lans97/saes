from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing, name="landing-home"),
    path("login/", views.login, name="landing-login"),
    path("register/", views.register, name="landing-register"),
]

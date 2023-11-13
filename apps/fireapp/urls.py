from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing, name="landing-home"),
    path("login/", views.login_view, name="landing-login"),
    path("register/", views.register, name="landing-register"),
    path("home/", views.home, name="home"),
    path("logout/", views.logout_view, name="logout"),

]

from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing, name="landing-home"),
    path("login/", views.login_view, name="landing-login"),
    path("register/", views.register, name="landing-register"),
    path("home/", views.home, name="home"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("settings/", views.settings_view, name="settings"),
    path("sensors/", views.sensors_view, name="sensors"),
    path("add-sensor/", views.add_sensor_view, name="add-sensor"),
    path("dashboard/<str:sensor_id>/", views.dashboard_view, name="dashboard"),
]

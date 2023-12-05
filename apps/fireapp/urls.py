from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
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
    path('download/', views.download_csv, name='download'),
    path('change-password/', PasswordChangeView.as_view(template_name='registration/password_change_form.html'), name='password_change'),
    path('change-password/done/', PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
]

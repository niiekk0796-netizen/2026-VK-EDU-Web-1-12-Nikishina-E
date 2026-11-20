from django.contrib.auth.views import LoginView
from django.urls import path

from . import views


app_name = "core"
urlpatterns = [
    path("login/", LoginView.as_view(template_name="core/login.html", redirect_authenticated_user=True), name="login"),
    path("signup/", views.signup, name="signup"),
    path("profile/", views.profile, name="profile"),
    path("logout/", views.logout, name="logout"),
]

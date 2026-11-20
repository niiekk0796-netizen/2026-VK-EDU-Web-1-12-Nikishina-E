from django.contrib.auth.views import LoginView
from django.urls import path

from . import views
from .forms import LoginForm


app_name = "core"
urlpatterns = [
    path("login/", LoginView.as_view(template_name="core/login.html", redirect_authenticated_user=True, authentication_form=LoginForm), name="login"),
    path("signup/", views.signup, name="signup"),
    path("profile/", views.profile, name="profile"),
    path("logout/", views.logout, name="logout"),
]

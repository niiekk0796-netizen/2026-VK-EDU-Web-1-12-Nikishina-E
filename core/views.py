from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST, require_http_methods

from .forms import ProfileForm, SignupForm
from .models import Profile


@require_http_methods(["GET", "POST"])
def signup(request):
    if request.user.is_authenticated:
        return redirect("questions:index")
    form = SignupForm(request.POST if request.method == "POST" else None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        auth_login(request, form.save())
        return redirect("questions:index")
    return render(request, "core/signup.html", {"form": form})


@login_required
@require_http_methods(["GET", "POST"])
def profile(request):
    account, _ = Profile.objects.get_or_create(user=request.user, defaults={"nickname": request.user.username[:40]})
    form = ProfileForm(request.POST if request.method == "POST" else None, request.FILES or None, instance=account)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Профиль сохранён.")
        return redirect("core:profile")
    return render(request, "core/profile.html", {"form": form})


@require_POST
def logout(request):
    target = request.POST.get("next", "/")
    auth_logout(request)
    if not url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        target = "/"
    return redirect(target)

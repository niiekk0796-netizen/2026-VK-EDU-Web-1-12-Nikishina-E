from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST, require_safe


@require_safe
def signup(request):
    return render(request, "core/signup.html")


@login_required
@require_safe
def profile(request):
    return render(request, "core/profile.html")


@require_POST
def logout(request):
    target = request.POST.get("next", "/")
    auth_logout(request)
    if not url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        target = "/"
    return redirect(target)

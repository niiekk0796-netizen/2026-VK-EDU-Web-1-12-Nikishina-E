from django.shortcuts import render
from django.views.decorators.http import require_safe


@require_safe
def login(request):
    return render(request, "core/login.html")


@require_safe
def signup(request):
    return render(request, "core/signup.html")


@require_safe
def profile(request):
    return render(request, "core/profile.html", {"demo_member": "Alex"})

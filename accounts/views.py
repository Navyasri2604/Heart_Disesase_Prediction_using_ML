"""
Views for the accounts application.
"""
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ProfileUpdateForm, RegistrationForm
from .models import UserActivityLog


def _log_activity(user, action, details="", request=None):
    """Helper to record user activity."""
    ip = None
    if request:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        ip = x_forwarded_for.split(",")[0] if x_forwarded_for else request.META.get("REMOTE_ADDR")
    UserActivityLog.objects.create(user=user, action=action, details=details, ip_address=ip)


def register(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect("dashboard:home")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        _log_activity(user, "Registered", "New account created", request)
        messages.success(request, "Welcome to HeartGuard, {}! Your account is ready.".format(user.first_name or user.username))
        return redirect("dashboard:home")
    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    """User profile view – update personal info."""
    # Ensure profile exists (safety net)
    from .models import UserProfile
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
    form = ProfileUpdateForm(request.POST or None, instance=profile_obj, user=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        _log_activity(request.user, "Updated Profile", "", request)
        messages.success(request, "Profile updated successfully.")
        return redirect("accounts:profile")
    return render(request, "accounts/profile.html", {"form": form})


@login_required
def activity_log(request):
    """View the user's activity log."""
    logs = UserActivityLog.objects.filter(user=request.user)[:50]
    return render(request, "accounts/activity_log.html", {"logs": logs})
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from accounts.models import UserProfile


def get_user_role(user):
    if not user.is_authenticated:
        return None
    if user.is_superuser:
        return UserProfile.Role.ADMIN
    profile = getattr(user, "profile", None)
    return profile.role if profile else UserProfile.Role.VIEWER


def role_required(*allowed_roles):
    """Restringe una vista a los roles indicados (los superusuarios siempre pasan)."""

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            role = get_user_role(request.user)
            if role in allowed_roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect("core:dashboard")

        return _wrapped

    return decorator

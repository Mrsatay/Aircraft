from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .utils import get_user_role


def role_required(*allowed_roles):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            role = get_user_role(request.user)
            request.session["role"] = role
            if role not in allowed_roles:
                messages.error(request, "Access denied for your role.")
                return redirect("dashboard:index")
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator

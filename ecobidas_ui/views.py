from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _


def render_error(request, status: int):
    """Render error template."""
    return render(request, f"{status}.html", status=status)


def page_not_found(request, exception=None):
    return render_error(request, 404)


def server_error(request):
    return render_error(request, 500)


def require_methods(*methods):
    """Only allow the listed HTTP methods and render the 405 page otherwise."""

    def decorator(view):
        @wraps(view)
        def wrapped_view(request, *args, **kwargs):
            if request.method not in methods:
                return render_error(request, 405)
            return view(request, *args, **kwargs)

        return wrapped_view

    return decorator


def home(request):
    return redirect("public:index")


def export(request):
    messages.warning(request, _("Export not implemented yet."))
    return render_error(request, 501)

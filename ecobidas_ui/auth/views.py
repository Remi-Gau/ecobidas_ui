import logging
import secrets

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext as _

from ecobidas_ui.auth import orcid
from ecobidas_ui.views import render_error, require_methods

logger = logging.getLogger(__name__)

SESSION_STATE = "orcid_state"
SESSION_NEXT = "orcid_next"


@require_methods("GET")
def login_page(request):
    if request.user.is_authenticated:
        return redirect(safe_next_url(request, request.GET.get("next")))
    return render(
        request,
        "auth/login.html",
        {"next": request.GET.get("next", ""), "orcid_configured": orcid.is_configured()},
    )


@require_methods("GET")
def orcid_login(request):
    """Send the user to ORCID to sign in."""
    if not orcid.is_configured():
        messages.error(request, _("Logging in with ORCID is not configured on this server."))
        return redirect("auth:login")

    state = secrets.token_urlsafe(32)
    request.session[SESSION_STATE] = state
    request.session[SESSION_NEXT] = safe_next_url(request, request.GET.get("next"))
    return redirect(orcid.authorize_url(callback_url(request), state))


@require_methods("GET")
def orcid_callback(request):
    """Log in the user that ORCID sends back, creating their account if needed."""
    state = request.session.pop(SESSION_STATE, None)
    next_url = request.session.pop(SESSION_NEXT, None) or reverse("home")

    if request.GET.get("error"):
        # for example: the user refused to authorize this site
        messages.warning(request, _("You were not logged in."))
        return redirect("auth:login")

    if not state or not secrets.compare_digest(state, request.GET.get("state", "")):
        return render_error(request, 400)

    try:
        orcid_id, name = orcid.get_identity(request.GET.get("code", ""), callback_url(request))
    except orcid.OrcidError as exc:
        logger.error(exc)
        messages.error(request, _("Logging in with ORCID failed. Please try again."))
        return redirect("auth:login")

    user, created = User.objects.get_or_create(username=orcid_id)
    if created:
        # users only log in with ORCID
        user.set_unusable_password()
    user.first_name = name[:150]
    user.save()

    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    messages.success(request, _("You are logged in."))
    return redirect(next_url)


@require_methods("GET")
def admin_login(request):
    """Log in to the admin site with ORCID."""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect(safe_next_url(request, request.GET.get("next")) or "admin:index")
        return render_error(request, 403)
    return redirect(f"{reverse('auth:orcid')}?{request.GET.urlencode()}")


def callback_url(request) -> str:
    """Return the URL ORCID sends the users back to: it must be registered on ORCID."""
    return request.build_absolute_uri(reverse("orcid_callback"))


def safe_next_url(request, url: str | None) -> str:
    """Only go back to pages of this site after logging in."""
    if url and url_has_allowed_host_and_scheme(
        url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return url
    return reverse("home")

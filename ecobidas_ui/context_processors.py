from django.conf import settings
from django.urls import translate_url

from ecobidas_ui._version import version as ui_version


def version(request):
    return {"version": ui_version}


def languages(request):
    """List the available languages with a link to the current page in each of them."""
    path = request.get_full_path()
    return {
        "languages": [
            {**info, "code": code, "url": translate_url(path, code)}
            for code, info in settings.LANGUAGES_INFO.items()
        ]
    }


def orcid(request):
    """Link to the ORCID profiles of the users."""
    return {"orcid_url": settings.ORCID_URL}

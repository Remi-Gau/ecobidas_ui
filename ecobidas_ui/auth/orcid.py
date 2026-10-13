"""Log in with ORCID (OAuth 2.0 authorization code flow).

See https://info.orcid.org/documentation/integration-guide/getting-started-with-your-orcid-integration/
"""

from urllib.parse import urlencode

import requests
from django.conf import settings


class OrcidError(Exception):
    """ORCID did not authenticate the user."""


def is_configured() -> bool:
    return bool(settings.ORCID_CLIENT_ID and settings.ORCID_CLIENT_SECRET)


def authorize_url(redirect_uri: str, state: str) -> str:
    """Return the ORCID page where users sign in and authorize this site."""
    query = urlencode(
        {
            "client_id": settings.ORCID_CLIENT_ID,
            "response_type": "code",
            # only read the ORCID iD and name of the user
            "scope": "/authenticate",
            "redirect_uri": redirect_uri,
            "state": state,
        }
    )
    return f"{settings.ORCID_URL}/oauth/authorize?{query}"


def get_identity(code: str, redirect_uri: str) -> tuple[str, str]:
    """Exchange the authorization code for the ORCID iD and name of the user."""
    try:
        response = requests.post(
            f"{settings.ORCID_URL}/oauth/token",
            data={
                "client_id": settings.ORCID_CLIENT_ID,
                "client_secret": settings.ORCID_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
            },
            headers={"Accept": "application/json"},
            timeout=10,
        )
        response.raise_for_status()
        content = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise OrcidError(f"Could not get a token from ORCID: {exc}") from exc

    orcid_id = content.get("orcid")
    if not orcid_id:
        raise OrcidError("ORCID did not return an ORCID iD.")
    return orcid_id, content.get("name") or ""

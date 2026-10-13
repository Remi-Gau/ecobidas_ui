from io import StringIO
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import pytest
import requests
from django.contrib.auth.models import User
from django.core.management import CommandError, call_command

ORCID_ID = "0000-0002-1825-0097"
CALLBACK = "/auth/orcid/callback"


@pytest.fixture(autouse=True)
def orcid_settings(settings):
    settings.ORCID_CLIENT_ID = "APP-TEST"
    settings.ORCID_CLIENT_SECRET = "secret"
    settings.ORCID_URL = "https://sandbox.orcid.org"


class FakeResponse:
    def __init__(self, content, status=200):
        self.content = content
        self.status = status

    def raise_for_status(self):
        if self.status >= 400:
            raise requests.HTTPError(f"{self.status} error")

    def json(self):
        return self.content


def start_login(client, next_url="/en/protocol/neurovault/participants"):
    """Go to ORCID and return the state to send back."""
    response = client.get("/en/auth/orcid", {"next": next_url})
    assert response.status_code == 302
    url = urlparse(response["Location"])
    assert f"{url.scheme}://{url.netloc}{url.path}" == "https://sandbox.orcid.org/oauth/authorize"
    query = parse_qs(url.query)
    assert query["client_id"] == ["APP-TEST"]
    assert query["scope"] == ["/authenticate"]
    assert query["redirect_uri"] == ["http://testserver/auth/orcid/callback"]
    return query["state"][0]


def orcid_returns(content, status=200):
    return patch("ecobidas_ui.auth.orcid.requests.post", return_value=FakeResponse(content, status))


def test_login_page(client):
    response = client.get("/en/auth/login")
    assert response.status_code == 200
    assert b"Log in with ORCID" in response.content


def test_login_page_without_orcid_configured(client, settings):
    settings.ORCID_CLIENT_ID = ""
    response = client.get("/en/auth/login")
    assert b"not configured" in response.content
    assert client.get("/en/auth/orcid")["Location"] == "/en/auth/login"


@pytest.mark.django_db
def test_login_creates_the_user(client):
    state = start_login(client)

    with orcid_returns({"orcid": ORCID_ID, "name": "Josiah Carberry"}) as post:
        response = client.get(CALLBACK, {"code": "abc", "state": state})

    assert post.call_args.kwargs["data"]["code"] == "abc"
    assert response.status_code == 302
    assert response["Location"] == "/en/protocol/neurovault/participants"

    user = User.objects.get(username=ORCID_ID)
    assert user.first_name == "Josiah Carberry"
    assert not user.has_usable_password()
    assert not user.is_staff

    page = client.get("/en/index").content.decode()
    assert "Josiah Carberry" in page
    assert "LOG OUT" in page


@pytest.mark.django_db
def test_login_existing_user(client):
    User.objects.create(username=ORCID_ID, first_name="Old name")
    state = start_login(client)

    with orcid_returns({"orcid": ORCID_ID, "name": "New name"}):
        client.get(CALLBACK, {"code": "abc", "state": state})

    assert User.objects.get().first_name == "New name"


@pytest.mark.django_db
def test_logout(client):
    client.force_login(User.objects.create(username=ORCID_ID))

    assert client.get("/en/auth/logout").status_code == 405
    response = client.post("/en/auth/logout")

    assert response.status_code == 302
    assert "LOG OUT" not in client.get("/en/index").content.decode()


@pytest.mark.parametrize("state", [None, "", "wrong"])
@pytest.mark.django_db
def test_callback_rejects_invalid_state(client, state):
    start_login(client)
    params = {"code": "abc"} if state is None else {"code": "abc", "state": state}

    with orcid_returns({"orcid": ORCID_ID}) as post:
        response = client.get(CALLBACK, params)

    assert response.status_code == 400
    post.assert_not_called()
    assert not User.objects.exists()


@pytest.mark.django_db
def test_callback_state_is_single_use(client):
    state = start_login(client)
    with orcid_returns({"orcid": ORCID_ID}):
        client.get(CALLBACK, {"code": "abc", "state": state})
    client.logout()

    with orcid_returns({"orcid": ORCID_ID}):
        response = client.get(CALLBACK, {"code": "abc", "state": state})

    assert response.status_code == 400


@pytest.mark.django_db
def test_user_refuses_authorization(client):
    start_login(client)
    response = client.get(CALLBACK, {"error": "access_denied"}, follow=True)
    assert b"You were not logged in." in response.content
    assert not User.objects.exists()


@pytest.mark.parametrize(
    "content, status",
    [({"error": "invalid_grant"}, 400), ({"access_token": "no orcid"}, 200), ("", 500)],
)
@pytest.mark.django_db
def test_orcid_fails(client, content, status):
    state = start_login(client)

    with orcid_returns(content, status):
        response = client.get(CALLBACK, {"code": "abc", "state": state}, follow=True)

    assert b"Logging in with ORCID failed" in response.content
    assert not User.objects.exists()


@pytest.mark.parametrize(
    "next_url", ["https://evil.example.com/", "//evil.example.com", "javascript:alert(1)"]
)
@pytest.mark.django_db
def test_only_redirect_to_this_site(client, next_url):
    state = start_login(client, next_url=next_url)

    with orcid_returns({"orcid": ORCID_ID}):
        response = client.get(CALLBACK, {"code": "abc", "state": state})

    assert response["Location"] == "/"


@pytest.mark.django_db
def test_admin_login(client):
    response = client.get("/admin/")
    assert response["Location"].startswith("/admin/login/")

    response = client.get(response["Location"])
    assert response["Location"] == "/en/auth/orcid?next=%2Fadmin%2F"

    client.force_login(User.objects.create(username=ORCID_ID))
    assert client.get("/admin/login/").status_code == 403

    call_command("make_admin", ORCID_ID, stdout=StringIO())
    assert client.get("/admin/").status_code == 200
    assert client.get("/admin/protocols/savedanswers/").status_code == 200

    call_command("make_admin", ORCID_ID, "--remove", stdout=StringIO())
    assert client.get("/admin/")["Location"].startswith("/admin/login/")


@pytest.mark.django_db
def test_make_admin_unknown_user():
    with pytest.raises(CommandError, match="must log in once first"):
        call_command("make_admin", ORCID_ID)

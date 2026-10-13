import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.visual

PAGES = {
    "index": "/en/index",
    "faq": "/en/faq/",
    "about": "/en/about/",
    "login": "/en/auth/login",
    "protocol_cobidas": "/en/protocol/cobidas",
    "activity_neurovault_participants": "/en/protocol/neurovault/participants",
    "activity_neurovault_mri_acquisition": "/en/protocol/neurovault/mri_acquisition",
    "generate": "/en/generate/",
}


@pytest.mark.parametrize("name", PAGES)
def test_page(name, live_server, page: Page, assert_snapshot):
    page.goto(f"{live_server.url}{PAGES[name]}", wait_until="networkidle")
    assert_snapshot(name)


@pytest.mark.django_db(transaction=True)
def test_logged_in(live_server, page: Page, assert_snapshot, client, django_user_model):
    user = django_user_model.objects.create(
        username="0000-0002-1825-0097", first_name="Josiah Carberry"
    )
    client.force_login(user)
    page.context.add_cookies(
        [{"name": "sessionid", "value": client.cookies["sessionid"].value, "url": live_server.url}]
    )

    page.goto(f"{live_server.url}/en/index", wait_until="networkidle")
    assert_snapshot("logged_in")

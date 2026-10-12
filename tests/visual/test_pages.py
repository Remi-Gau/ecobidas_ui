import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.visual

PAGES = {
    "index": "/en/index",
    "faq": "/en/faq/",
    "about": "/en/about/",
    "login": "/en/auth/login",
    "register": "/en/auth/register",
    "protocol_cobidas": "/en/protocol/cobidas",
    "activity_neurovault_participants": "/en/protocol/neurovault/participants",
    "activity_neurovault_mri_acquisition": "/en/protocol/neurovault/mri_acquisition",
    "generate": "/en/generate/",
    "page_not_found": "/en/protocol/unknown",
}


@pytest.mark.parametrize("name", PAGES)
def test_page(name, live_server, page: Page, assert_snapshot):
    page.goto(f"{live_server.url}{PAGES[name]}", wait_until="networkidle")
    assert_snapshot(name)

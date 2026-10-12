"""Fixtures for the visual regression tests.

Screenshots of the pages are compared to the reference images in ``snapshots/``.
On failure, the new screenshot and an image of the differences
are saved in ``snapshot_failures/``.

The reference images are only valid for the playwright docker image
they were generated with: see the makefile to run or update them.
"""

import os
from collections.abc import Callable
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image
from pixelmatch.contrib.PIL import pixelmatch
from playwright.sync_api import Page

from ecobidas_ui import context_processors

# playwright runs an event loop that would make django refuse database access
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

SNAPSHOTS_DIR = Path(__file__).parent / "snapshots"
FAILURES_DIR = Path(__file__).parent / "snapshot_failures"

# fraction of pixels allowed to differ from the reference image:
# rendering is deterministic in the playwright docker image
MAX_DIFF_RATIO = 0


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--update-snapshots",
        action="store_true",
        default=False,
        help="Overwrite the reference images of the visual regression tests.",
    )


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 800},
        "device_scale_factor": 1,
        "color_scheme": "light",
        "locale": "en-US",
        "timezone_id": "UTC",
    }


@pytest.fixture(autouse=True)
def fixed_version(monkeypatch: pytest.MonkeyPatch) -> None:
    """Display the same version on every commit (shown in the footer)."""
    monkeypatch.setattr(context_processors, "ui_version", "0.0.0")


@pytest.fixture
def assert_snapshot(page: Page, request: pytest.FixtureRequest) -> Callable[[str], None]:
    """Compare a full page screenshot to its reference image."""

    def _assert_snapshot(name: str) -> None:
        screenshot = page.screenshot(
            full_page=True,
            animations="disabled",
            caret="hide",
        )

        reference = SNAPSHOTS_DIR / f"{name}.png"
        if request.config.getoption("--update-snapshots") or not reference.exists():
            SNAPSHOTS_DIR.mkdir(exist_ok=True)
            reference.write_bytes(screenshot)
            if not request.config.getoption("--update-snapshots"):
                pytest.fail(f"No reference image for '{name}': it was created at {reference}.")
            return

        actual = Image.open(BytesIO(screenshot)).convert("RGBA")
        expected = Image.open(reference).convert("RGBA")

        FAILURES_DIR.mkdir(exist_ok=True)
        if actual.size != expected.size:
            actual.save(FAILURES_DIR / f"{name}.png")
            pytest.fail(
                f"'{name}' changed size: {expected.size} -> {actual.size}. "
                f"See {FAILURES_DIR / name}.png"
            )

        diff = Image.new("RGBA", actual.size)
        nb_diff_pixels = pixelmatch(expected, actual, diff, threshold=0.1)
        if nb_diff_pixels / (actual.width * actual.height) > MAX_DIFF_RATIO:
            actual.save(FAILURES_DIR / f"{name}.png")
            diff.save(FAILURES_DIR / f"{name}_diff.png")
            pytest.fail(
                f"'{name}' differs from its reference image ({nb_diff_pixels} pixels). "
                f"See {FAILURES_DIR / name}.png and {FAILURES_DIR / name}_diff.png"
            )

    return _assert_snapshot

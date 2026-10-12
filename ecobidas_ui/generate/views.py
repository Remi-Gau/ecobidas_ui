"""Generate a method section from the checklist."""

import json

from django.conf import settings
from django.contrib import messages
from django.http import FileResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from markdownify import markdownify as md

from ecobidas_ui.views import require_methods


def dummmy_data():
    with open(
        settings.ROOT_DIR / ".." / "inputs" / "bids_template" / "task-auditoryLocalizer_bold.json"
    ) as f:
        data = json.load(f)
    return data


@require_methods("GET", "POST")
def generate(request):
    messages.warning(
        request,
        _(
            """This page was generated using dummy data.
        In the final version the content of this page should adapt to the values you inputted in the checklist."""
        ),
    )
    return render(request, "generate/index.html", dummmy_data())


@require_methods("GET")
def download(request):
    tmp = md(render_to_string("generate/report.html", request=request), heading_style="ATX")
    report = settings.UPLOAD_FOLDER / "report.md"
    with open(report, "w") as f:
        f.write(tmp)
    return FileResponse(open(report, "rb"), content_type="text/markdown")

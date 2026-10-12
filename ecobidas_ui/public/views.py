"""Public section, including homepage and signup."""

import json

from django.conf import settings
from django.shortcuts import render

from ecobidas_ui.views import require_methods


@require_methods("GET", "POST")
def index(request):
    """Home page."""
    return render(request, "public/index.html")


@require_methods("GET")
def faq(request):
    with open(settings.ROOT_DIR / "static" / "json" / "faq.json") as f:
        data = json.load(f)
    return render(request, "public/faq.html", {"data": data})


@require_methods("GET")
def about(request):
    """About page."""
    return render(request, "public/about.html")

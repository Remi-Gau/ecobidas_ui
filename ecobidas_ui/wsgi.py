"""WSGI config for ecobidas_ui."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecobidas_ui.settings")

application = get_wsgi_application()

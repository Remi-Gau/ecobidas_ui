from importlib.util import find_spec

import pytest
from django.test import Client

# the visual regression tests need the 'visual' dependency group
if find_spec("playwright") is None:
    collect_ignore = ["visual"]


@pytest.fixture()
def client():
    return Client()

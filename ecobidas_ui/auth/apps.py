from django.apps import AppConfig


class AuthConfig(AppConfig):
    name = "ecobidas_ui.auth"
    # avoid clashing with django.contrib.auth
    label = "ecobidas_auth"

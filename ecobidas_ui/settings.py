from pathlib import Path

from environs import Env

env = Env()
env.read_env()

ROOT_DIR = Path(__file__).parent

# ---- SETUP INSTRUCTIONS AND APP BEHAVIOR ####

# ------ App-level configuration ###
DEBUG = env.bool("DEBUG", False)

PROTOTYPE = True

SECRET_KEY = env.str("SECRET_KEY")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", ["localhost", "127.0.0.1", "[::1]", "backend"])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_bootstrap5",
    "ecobidas_ui.public",
    "ecobidas_ui.auth",
    "ecobidas_ui.protocols",
    "ecobidas_ui.generate",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ecobidas_ui.urls"
WSGI_APPLICATION = "ecobidas_ui.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [ROOT_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.contrib.messages.context_processors.messages",
                "ecobidas_ui.context_processors.version",
                "ecobidas_ui.context_processors.languages",
                "ecobidas_ui.context_processors.orcid",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": env.path("DATABASE_PATH", ROOT_DIR.parent / "db.sqlite3"),
        "OPTIONS": {
            # let the gunicorn workers write concurrently without "database is locked" errors
            "init_command": "PRAGMA journal_mode=WAL;",
            "transaction_mode": "IMMEDIATE",
            "timeout": 20,
        },
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# User accounts
LOGIN_URL = "auth:login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"
# users log in with ORCID: register this site at https://orcid.org/developer-tools
# with the redirect URI https://<your domain>/auth/orcid/callback
ORCID_CLIENT_ID = env.str("ORCID_CLIENT_ID", "")
ORCID_CLIENT_SECRET = env.str("ORCID_CLIENT_SECRET", "")
# use https://sandbox.orcid.org to test with sandbox accounts
ORCID_URL = env.str("ORCID_URL", "https://orcid.org").rstrip("/")

# Static content
STATIC_URL = "static/"
STATICFILES_DIRS = [ROOT_DIR / "static"]
STATIC_ROOT = ROOT_DIR.parent / "staticfiles"

# Map the "error" message level to the bootstrap "danger" alert class
MESSAGE_TAGS = {40: "danger"}

# Internationalization
USE_I18N = True
LANGUAGE_CODE = "en"
LOCALE_PATHS = [ROOT_DIR / "locale"]

LANGUAGES_INFO = {
    "zh-hans": {"display_name": "中文", "flag_code": "cn"},
    "de": {"display_name": "Deutsch", "flag_code": "de"},
    "en": {"display_name": "English", "flag_code": "us"},
    "es": {"display_name": "Español", "flag_code": "es"},
    "fr": {"display_name": "Français", "flag_code": "fr"},
}
LANGUAGES = [(code, info["display_name"]) for code, info in LANGUAGES_INFO.items()]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {"ecobidas_ui": {"handlers": ["console"], "level": "INFO"}},
}

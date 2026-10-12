from pathlib import Path

from environs import Env

env = Env()
env.read_env()

ROOT_DIR = Path(__file__).parent

UPLOAD_FOLDER = ROOT_DIR / "tmp"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# ---- SETUP INSTRUCTIONS AND APP BEHAVIOR ####

# ------ App-level configuration ###
DEBUG = env.bool("DEBUG", False)

PROTOTYPE = True

SECRET_KEY = env.str("SECRET_KEY")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", ["localhost", "127.0.0.1", "[::1]", "backend"])

INSTALLED_APPS = [
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
                "django.template.context_processors.i18n",
                "django.contrib.messages.context_processors.messages",
                "ecobidas_ui.context_processors.version",
                "ecobidas_ui.context_processors.languages",
            ],
        },
    },
]

# No user accounts yet: keep sessions in signed cookies so no database is needed.
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ROOT_DIR.parent / "db.sqlite3",
    }
}

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

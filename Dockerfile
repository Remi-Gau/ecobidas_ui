FROM python:3.12.15-bookworm

# gettext is needed to compile the translations
RUN apt-get update \
    && apt-get install -y --no-install-recommends gettext \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.13.0 /uv /uvx /bin/

# includes .git: needed for the submodules and the hatch-vcs version
COPY . app/

WORKDIR /app

RUN git submodule update --init --recursive && uv sync --locked --no-dev

ENV PATH="/app/.venv/bin:$PATH"

# the secret key is only needed to load the settings
RUN SECRET_KEY=build-only python manage.py collectstatic --noinput \
    && cd ecobidas_ui && django-admin compilemessages

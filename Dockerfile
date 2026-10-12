FROM python:3.12.15-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.13.0 /uv /uvx /bin/

COPY . app/

# need git tags for hatch-vcs
COPY .git app/.git

WORKDIR /app

RUN git submodule update --init --recursive && uv sync --locked --no-dev

ENV PATH="/app/.venv/bin:$PATH"

RUN python manage.py collectstatic --noinput

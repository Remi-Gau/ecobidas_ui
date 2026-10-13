# 🚧 eCOBIDAS UI 🚧

🎉

This contains the code for a UI to run the eCOBIDAS checklist using Django.

<img src="./images/landing.png" width=500px>
<img src="./images/import-from-bids.png" width=500px>
<img src="./images/report.png" width=500px>

## Install

Get the repo and all its submodules.

```bash
git clone --recurse-submodules https://github.com/Remi-Gau/ecobidas_ui.git
```

Dependencies are managed with [uv](https://docs.astral.sh/uv/)
and pinned in `uv.lock`.
Install them (including the test and dev tools) in a virtual environment with:

```bash
uv sync
```

To update the pinned dependencies:

```bash
tox run -e update_dependencies  # or: uv lock --upgrade
```

## Run with docker compose

The site is served by gunicorn behind an nginx proxy on <http://localhost>.

Set a secret key (and optionally the allowed hosts) in a `.env` file next to `docker-compose.yml`:

```bash
echo "SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')" > .env
# ALLOWED_HOSTS=example.org  # comma separated, defaults to localhost,127.0.0.1
docker compose up --build
```

The database (user accounts and saved answers) is kept in the `db` volume.

## User accounts

Users log in with their [ORCID iD](https://orcid.org): the site stores no passwords.
An account is created the first time someone logs in.

1. Register the site in the [ORCID developer tools](https://orcid.org/developer-tools)
   with the redirect URI `https://<your domain>/auth/orcid/callback`.
   To test, use the [ORCID sandbox](https://sandbox.orcid.org/developer-tools) instead
   and set `ORCID_URL=https://sandbox.orcid.org`.
2. Add the client ID and secret to your `.env`:

   ```bash
   ORCID_CLIENT_ID=APP-XXXXXXXXXXXXXXXX
   ORCID_CLIENT_SECRET=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   ```

To give someone access to the admin site (`/admin/`), let them log in once, then run:

```bash
docker compose exec backend python manage.py make_admin 0000-0002-1825-0097
# or locally: uv run python manage.py make_admin 0000-0002-1825-0097
```

## Run the tests

```bash
tox run -e test  # or: uv run pytest
```

## Serve locally

```bash
uv run python manage.py migrate
uv run python manage.py runserver
```

Open the link `http://127.0.0.1:8000`

## Visual regression tests

Screenshots of the main pages are compared to the reference images in `tests/visual/snapshots`.
They run in the playwright docker image, so that the screenshots
do not depend on the browsers and fonts installed on your machine (requires docker).

```bash
uv sync           # generates ecobidas_ui/_version.py used by the tests
make visual       # on failure, see the screenshots in tests/visual/snapshot_failures
make visual_update  # update the reference images after an intended visual change
```

To add a page, add it to `PAGES` in `tests/visual/test_pages.py` and run `make visual_update`.

## Linting and type checking

Code is linted and formatted with [ruff](https://docs.astral.sh/ruff/),
templates with [djLint](https://djlint.com/),
and types are checked with [pyrefly](https://pyrefly.org/),
all via [pre-commit](https://pre-commit.com/).

```bash
tox run -e lint       # or: uv run pre-commit run --all-files
tox run -e typecheck  # or: uv run pyrefly check
```

## Translations

Translations live in `ecobidas_ui/locale`.
Updating and compiling them requires [gettext](https://www.gnu.org/software/gettext/).

```bash
source .venv/bin/activate
make messages          # extract new strings into the .po files
make compile_messages  # compile the .po files so Django can use them
```

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

## Run the tests

```bash
tox run -e test  # or: uv run pytest
```

## Serve locally

```bash
uv run python manage.py runserver
```

Open the link `http://127.0.0.1:8000`

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

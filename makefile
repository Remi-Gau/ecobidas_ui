.PHONY: messages compile_messages

# requires gettext to be installed
messages:
	cd ecobidas_ui && django-admin makemessages -l de -l fr -l es -l zh_Hans

compile_messages:
	cd ecobidas_ui && django-admin compilemessages

# sudo snap install poedit

install:
	git submodule update --init --recursive && git submodule update --recursive
	uv sync

# Visual regression tests
#
# Run in the playwright docker image so that the screenshots
# do not depend on the browsers and fonts installed on the host.
# Keep the image version in sync with the playwright version in pyproject.toml.
PLAYWRIGHT_IMAGE := mcr.microsoft.com/playwright/python:v1.63.0-noble
VISUAL_TESTS := docker run --rm --user "$$(id -u):$$(id -g)" \
	-v "$(CURDIR):/app" -w /app \
	-e HOME=/tmp -e UV_PROJECT_ENVIRONMENT=/tmp/venv \
	-e UV_PYTHON=python3.12 -e UV_PYTHON_DOWNLOADS=never \
	$(PLAYWRIGHT_IMAGE) sh -c \
	"pip install --quiet --user --break-system-packages uv && \
	/tmp/.local/bin/uv sync --quiet --locked --no-install-project --no-default-groups --group visual && \
	/tmp/.local/bin/uv run --no-sync pytest -m visual tests/visual $(PYTEST_ARGS)"

.PHONY: visual visual_update

## run the visual regression tests (requires ecobidas_ui/_version.py: run 'uv sync' first)
visual:
	$(VISUAL_TESTS)

## update the reference images of the visual regression tests
visual_update:
	$(MAKE) visual PYTEST_ARGS=--update-snapshots

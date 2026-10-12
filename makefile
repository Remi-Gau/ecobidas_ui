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

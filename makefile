.PHONY: messages.pot

messages.pot:
	pybabel extract -F babel.cfg -o messages.pot .

# pybabel init -i messages.pot -d ecobidas_ui/translations -l fr
# pybabel update -i messages.pot -d ecobidas_ui/translations -l fr

# sudo snap install poedit
# pybabel compile -d ecobidas_ui/translations

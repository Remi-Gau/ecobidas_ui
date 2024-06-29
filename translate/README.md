# Translating eCOBIDAS

## Extract strings to translte from jsonld

```bash
python extract.py path
```

This will extract all the strings in english (`"en": "string to extract"`) from the jsonld
and save them in a `path/message.pot` file.

## create .po file to "host" translations

```bash
pybabel init --input-file path/message.pot --output-dir translations --locale fr
```
This will create file in `translations/fr/LC_MESSAGES/messages.po` to host the french translations.

Change the locale to create different translations.

### update .po files if new string to translate have been added

Using the short version for each parameter here.
This will update the `.po` file in case you extracted new strings or removed some in the `.pot` file.

```bash
pybabel update -i messages.pot -d translations -l fr
```

## automate translations

```bash
python translate.py path_to_po_file
```

## check translattions

use podeit (or another software to work with po files) to translate

https://poedit.net/

## update original jsonld

```bash
python inject.py
```

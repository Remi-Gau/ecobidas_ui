import sys
from pathlib import Path

import polib
from googletrans import Translator
from rich import print

TARGET_LANGUAGES = ["fr"]

translator = Translator()


def translate_string(msgid: str, dest_language: str = "fr") -> str:

    try:
        translation = translator.translate(msgid, dest=dest_language)
        print(f"  {msgid}: [green]SUCCESS")
    except TypeError:
        print(f"  {msgid}: [red]FAILED")
        return ""

    return translation.text


def translate_po_file(po: polib.POFile, dest_language: str) -> polib.POFile:
    # Populate translations dictionary with msgid and msgstr pairs
    for entry in po:
        # Extract the English original (msgid) and generate a translation (msgstr)
        msgid = entry.msgid
        entry.msgstr = translate_string(msgid, dest_language=dest_language)

    return po


def main():

    input_folder = Path(sys.argv[1])

    for dest_language in TARGET_LANGUAGES:

        print(f"translating: {dest_language}")

        po_file = input_folder / dest_language / "LC_MESSAGES" / "messages.po"

        # Load translations from the .po file
        po = polib.pofile(po_file)
        po = translate_po_file(po, dest_language)

        # Write updated content to the .po file
        po.save(po_file)


if __name__ == "__main__":
    main()

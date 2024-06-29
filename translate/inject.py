import json
from pathlib import Path

import polib
from rich import print

TARGET_LANGUAGES = ["fr"]


def set_value_at_path(json_data: dict, path: str, value) -> None:
    parts = path.split(".")
    current_level = json_data

    for i, part in enumerate(parts):
        if "[" in part and "]" in part:
            part, index = part.split("[")
            index = int(index[:-1])
            if i == len(parts) - 1:
                current_level[part][index] = value
            else:
                current_level = current_level[part][index]

        else:
            if i == len(parts) - 1:
                current_level[part] = value
            else:
                current_level = current_level[part]


def update_jsonld_with_translations(po_file, dest_language):
    # Load translations from the .po file
    po = polib.pofile(po_file)

    # Populate translations dictionary with msgid and msgstr pairs
    for entry in po:

        # Extract the path from the comment
        comments = entry.comment.split(",\n")
        for idx in range(0, len(comments) - 1, 2):

            if entry.msgstr != "":

                jsonld_file = comments[idx].replace("Extracted from file:\n", "")

                path = comments[idx + 1].split("path: ")[-1].strip()

                # drop the 'en' language and replace by the destination language
                path = path.split(".")
                path = path[:-1]
                path.append(dest_language)
                path = ".".join(path)

                # Load the original jsonld file
                with open(jsonld_file, encoding="utf-8") as f:
                    jsonld_data = jsonld_data = json.load(f)

                set_value_at_path(jsonld_data, path, entry.msgstr)

                # Write updated jsonld data back to the file
                with open(jsonld_file, "w", encoding="utf-8") as f:
                    json.dump(jsonld_data, f, indent=4, ensure_ascii=False)


def update_jsonld(jsonld_data, translations, dest_language):
    ...

    for key in translations:
        print(key)

    # Ensure jsonld_data is a dictionary or list of dictionaries
    if isinstance(jsonld_data, dict):
        # Traverse dictionary
        for key, value in jsonld_data.items():
            if isinstance(value, (dict, list)):
                value = update_jsonld(value, translations, dest_language)
                jsonld_data[key] = value
            elif key in translations:
                # Update value with translations if key matches
                if "en" in translations[key]:
                    jsonld_data[key][dest_language] = translations[key][dest_language]

    elif isinstance(jsonld_data, list):
        tmp = [update_jsonld(item, translations, dest_language) for item in jsonld_data]
        jsonld_data = tmp

    return jsonld_data


# Example usage:
if __name__ == "__main__":

    # input_folder = Path(sys.argv[1])
    input_folder = Path("translate/translations")

    for dest_language in TARGET_LANGUAGES:

        print(f"translating: {dest_language}")

        po_file = input_folder / dest_language / "LC_MESSAGES" / "messages.po"

        # Load translations from the .po file
        po = polib.pofile(po_file)

        update_jsonld_with_translations(po_file, dest_language)


def test_set_value_at_path():

    json_data = {}

    set_value_at_path(json_data, "ui.addProperties[12].prefLabel.en", "bla")

    print(json_data)

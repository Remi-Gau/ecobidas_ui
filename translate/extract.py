import json
import sys
from pathlib import Path

from babel.messages.catalog import Catalog
from babel.messages.pofile import write_po


def load_jsonld(file_path):
    with open(file_path, encoding="utf-8") as f:
        return json.load(f)


def extract_english_text_for_translation(data, catalog, parent_key="", file_path=""):

    if isinstance(data, dict):
        for k, v in data.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, (dict, list)):
                extract_english_text_for_translation(v, catalog, new_key, file_path)
            elif k == "en" and isinstance(v, str) and v.strip():
                comment = f"Extracted from file: {file_path}, path: {new_key}"
                catalog.add(v, None, locations=[(new_key, None)], auto_comments=[comment])

    elif isinstance(data, list):
        for i, item in enumerate(data):
            new_key = f"{parent_key}[{i}]"
            extract_english_text_for_translation(item, catalog, new_key, file_path)

    return catalog


def main():
    input_folder = Path(
        "/home/remi/github/ecobidas_ui/ecobidas_central/cobidas_schema/schemas/neurovault"
    )
    if len(sys.argv) > 1:
        input_folder = Path(sys.argv[1])

    catalog = Catalog()

    files = input_folder.glob("**/*.jsonld")
    for file in files:
        # Load JSON-LD content from example.jsonld
        json_ld = load_jsonld(file)
        catalog = extract_english_text_for_translation(json_ld, catalog, file_path=file)

    output_file = input_folder / "messages.pot"
    with open(output_file, "wb") as pot_file:
        write_po(pot_file, catalog)


if __name__ == "__main__":
    main()

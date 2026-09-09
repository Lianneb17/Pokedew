import json
import re
from pathlib import Path

# Map waarin de JSON-bestanden staan
ROOT_FOLDER = Path(__file__).resolve().parent / "assets"

# Bestaand vertaalbestand
TRANSLATION_FILE = Path(__file__).resolve().parent / "i18n" / "default.json"


def collect_i18n_keys(root_folder):
    """Zoek alle {{i18n:Key}} verwijzingen in JSON-bestanden."""
    pattern = re.compile(r"\{\{i18n:([^}|]+)(?:\|[^}]*)?\}\}")
    keys = set()

    for json_file in root_folder.rglob("*.json"):
        # Het vertaalbestand zelf niet doorzoeken
        if json_file.resolve() == TRANSLATION_FILE.resolve():
            continue

        try:
            text = json_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            print(f"Kan niet lezen: {json_file}")
            print(f"  {e}")
            continue

        matches = pattern.findall(text)

        for key in matches:
            keys.add(key.strip())

    return keys


def update_translation_file(keys):
    """Voeg ontbrekende keys toe aan het bestaande vertaalbestand."""

    try:
        with TRANSLATION_FILE.open("r", encoding="utf-8") as file:
            translations = json.load(file)
    except FileNotFoundError:
        print(f"Vertaalbestand niet gevonden: {TRANSLATION_FILE}")
        return
    except json.JSONDecodeError as e:
        print(f"Vertaalbestand bevat ongeldige JSON: {e}")
        return

    missing_keys = sorted(keys - translations.keys())

    if not missing_keys:
        print("Geen nieuwe vertalingen gevonden.")
        return

    for key in missing_keys:
        translations[key] = ""

    with TRANSLATION_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            translations,
            file,
            ensure_ascii=False,
            indent=2
        )
        file.write("\n")

    print(f"{len(missing_keys)} nieuwe keys toegevoegd:")

    for key in missing_keys:
        print(f"  {key}")


def main():
    print("Vertalingen verzamelen...")

    keys = collect_i18n_keys(ROOT_FOLDER)

    print(f"{len(keys)} unieke i18n-keys gevonden.")

    update_translation_file(keys)


if __name__ == "__main__":
    main()
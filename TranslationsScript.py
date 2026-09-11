import json
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

# Map waarin alle JSON-bestanden gezocht worden
ROOT_FOLDER = Path(__file__).resolve().parent / "assets"

# Bestaand vertaalbestand
TRANSLATION_FILE = Path(__file__).resolve().parent / "i18n" / "default.json"

# ============================================================
# I18N KEY COLLECTION
# ============================================================

def collect_i18n_keys(text):
    """
    Zoek alle {{i18n:Key}}-verwijzingen in tekst.

    Ondersteunt:
        {{i18n:Key}}

    En:
        {{i18n:Key |parameter=x}}

    En geneste i18n-verwijzingen:
        {{i18n:Key |parameter={{i18n:OtherKey}}}}
    """

    keys = set()
    marker = "{{i18n:"

    pos = 0

    while True:
        start = text.find(marker, pos)

        if start == -1:
            break

        key_start = start + len(marker)

        # Zoek waar de key eindigt.
        pipe = text.find("|", key_start)
        end = text.find("}}", key_start)

        if pipe != -1 and (end == -1 or pipe < end):
            key_end = pipe
        else:
            key_end = end

        if key_end == -1:
            break

        key = text[key_start:key_end].strip()

        if key:
            keys.add(key)

        # Niet direct na de volledige i18n-tag verdergaan,
        # zodat geneste i18n-tags ook gevonden worden.
        pos = key_start

    return keys


# ============================================================
# SEARCH JSON FILES
# ============================================================

def collect_keys_from_json_files(root_folder):
    """
    Doorzoek alle JSON-bestanden onder root_folder
    en verzamel alle unieke i18n-keys.
    """

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

        file_keys = collect_i18n_keys(text)

        if file_keys:
            print(f"{json_file}: {len(file_keys)} keys gevonden")

        keys.update(file_keys)

    return keys


# ============================================================
# LOAD TRANSLATIONS
# ============================================================

def load_translation_file():
    """
    Laad het bestaande vertaalbestand.
    """

    if not TRANSLATION_FILE.exists():
        print()
        print("Vertaalbestand niet gevonden:")
        print(f"  {TRANSLATION_FILE}")
        return None

    try:
        with TRANSLATION_FILE.open("r", encoding="utf-8") as file:
            translations = json.load(file)

    except json.JSONDecodeError as e:
        print()
        print("Het vertaalbestand bevat ongeldige JSON:")
        print(f"  {e}")
        return None

    except OSError as e:
        print()
        print("Kan het vertaalbestand niet lezen:")
        print(f"  {e}")
        return None

    if not isinstance(translations, dict):
        print()
        print("Het vertaalbestand moet een JSON-object zijn.")
        print('Bijvoorbeeld: {"Key": "Vertaling"}')
        return None

    return translations


# ============================================================
# UPDATE TRANSLATION FILE
# ============================================================

def update_translation_file(translations, used_keys):
    """
    Voeg ontbrekende keys toe aan het vertaalbestand.

    Bestaande keys en vertalingen worden niet gewijzigd.

    Geeft daarnaast ongebruikte vertaalkeys terug.
    """

    translation_keys = set(translations.keys())

    # Keys die wel gebruikt worden maar nog niet in de vertalingen staan
    missing_keys = sorted(used_keys - translation_keys)

    # Keys die in de vertalingen staan maar nergens gebruikt worden
    unused_keys = sorted(translation_keys - used_keys)

    if missing_keys:
        print()
        print("----------------------------------------")
        print(f"{len(missing_keys)} nieuwe keys gevonden:")
        print("----------------------------------------")

        for key in missing_keys:
            print(f"  + {key}")
            translations[key] = ""

        try:
            with TRANSLATION_FILE.open("w", encoding="utf-8") as file:
                json.dump(
                    translations,
                    file,
                    ensure_ascii=False,
                    indent=2
                )
                file.write("\n")

        except OSError as e:
            print()
            print("Kan het vertaalbestand niet opslaan:")
            print(f"  {e}")
            return unused_keys

        print()
        print(f"{len(missing_keys)} keys toegevoegd.")

    else:
        print()
        print("Geen nieuwe vertalingen gevonden.")

    return unused_keys


# ============================================================
# REPORT UNUSED KEYS
# ============================================================

def report_unused_keys(unused_keys):
    """
    Toon vertaalkeys die nergens meer gebruikt worden.
    """

    print()
    print("========================================")
    print("ONGEBRUIKTE VERTALINGSKEYS")
    print("========================================")

    if not unused_keys:
        print("Geen ongebruikte keys gevonden.")
        return

    print()
    print(f"{len(unused_keys)} keys worden nergens gebruikt:")
    print()

    for key in unused_keys:
        print(f"  - {key}")

    print()
    print("Deze keys zijn niet automatisch verwijderd.")


# ============================================================
# MAIN
# ============================================================

def main():
    print("========================================")
    print("Pokedew i18n key collector")
    print("========================================")
    print()
    print(f"Zoekmap:")
    print(f"  {ROOT_FOLDER}")
    print()
    print(f"Vertaalbestand:")
    print(f"  {TRANSLATION_FILE}")
    print()

    if not ROOT_FOLDER.exists():
        print("De zoekmap bestaat niet.")
        return

    # Bestaande vertalingen laden
    translations = load_translation_file()

    if translations is None:
        return

    # Alle gebruikte i18n-keys verzamelen
    used_keys = collect_keys_from_json_files(ROOT_FOLDER)

    print()
    print("----------------------------------------")
    print(f"Totaal gebruikte unieke keys: {len(used_keys)}")
    print(f"Totaal bestaande vertalingskeys: {len(translations)}")
    print("----------------------------------------")

    # Vertalingen bijwerken en ongebruikte keys bepalen
    unused_keys = update_translation_file(
        translations,
        used_keys
    )

    # Rapport ongebruikte keys
    report_unused_keys(unused_keys)

    print()
    print("========================================")
    print("Klaar.")
    print("========================================")


if __name__ == "__main__":
    main()
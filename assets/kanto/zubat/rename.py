import json
from pathlib import Path


# Alles staat in dezelfde map als dit script
FOLDER = Path(__file__).parent


def main():
    # Zoek het JSON-bestand dat eindigt op "data.json"
    json_files = list(FOLDER.glob("*data.json"))

    if not json_files:
        print("FOUT: Geen bestand gevonden dat eindigt op 'data.json'.")
        return

    if len(json_files) > 1:
        print("FOUT: Meerdere bestanden gevonden die eindigen op 'data.json':")
        for file in json_files:
            print(f"  - {file.name}")
        return

    json_file = json_files[0]

    # JSON lezen
    try:
        with json_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"FOUT: Ongeldige JSON: {e}")
        return

    # Eerste Change pakken
    changes = data.get("Changes", [])

    if not changes:
        print("FOUT: Geen Changes gevonden.")
        return

    target = changes[0].get("Target", "")

    if not target:
        print("FOUT: Geen Target gevonden in de eerste Change.")
        return

    # Namen uit Target halen
    names = []

    for entry in target.split(","):
        entry = entry.strip()

        if "/" not in entry:
            continue

        # Alleen alles NA de /
        name = entry.split("/", 1)[1].strip()

        if name:
            names.append(name)

    # PNG-bestanden zoeken
    images = sorted(
        [
            file
            for file in FOLDER.iterdir()
            if file.is_file()
            and file.suffix.lower() == ".png"
        ],
        key=lambda x: x.name.lower()
    )

    print(f"JSON-bestand:          {json_file.name}")
    print(f"Benodigde namen:       {len(names)}")
    print(f"Gevonden afbeeldingen: {len(images)}")

    # Eerst controleren of er genoeg afbeeldingen zijn
    if len(images) < len(names):
        print()
        print("NIET UITGEVOERD!")
        print(f"Er zijn {len(names)} afbeeldingen nodig.")
        print(f"Er zijn {len(images)} afbeeldingen gevonden.")
        print(f"Er ontbreken {len(names) - len(images)} afbeeldingen.")
        return

    # Controleer vooraf op dubbele doelbestanden
    target_files = [FOLDER / f"{name}.png" for name in names]

    duplicates = {
        path.name
        for path in target_files
        if target_files.count(path) > 1
    }

    if duplicates:
        print()
        print("NIET UITGEVOERD!")
        print("De volgende namen komen meerdere keren voor:")
        for name in sorted(duplicates):
            print(f"  - {name}")
        return

    # Controleer of doelbestanden al bestaan
    conflicts = []

    for image, target_file in zip(images, target_files):
        if target_file.exists() and target_file != image:
            conflicts.append(target_file.name)

    if conflicts:
        print()
        print("NIET UITGEVOERD!")
        print("De volgende bestanden bestaan al:")
        for name in conflicts:
            print(f"  - {name}")
        return

    # Alles is gecontroleerd, nu pas hernoemen
    print()
    print("Hernoemen:")

    for image, target_file in zip(images, target_files):
        print(f"  {image.name} -> {target_file.name}")
        image.rename(target_file)

    print()
    print(f"Klaar! {len(names)} afbeeldingen hernoemd.")


if __name__ == "__main__":
    main()
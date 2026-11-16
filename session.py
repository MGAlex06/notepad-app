import json
import os
from pathlib import Path

import strings


def session_path():
    """Unde ținem sesiunea: %APPDATA%\\NotepadApp\\session.json."""
    return Path(os.environ["APPDATA"]) / "NotepadApp" / "session.json"


def save_session(path, files, active, width, height, language):
    """Scrie sesiunea în fișierul JSON `path`.

    `files` = lista căilor fișierelor deschise, în ordinea filelor.
    `active` = calea fișierului din fila activă (None dacă era „Fără titlu”).
    `width`, `height` = dimensiunea ferestrei, în pixeli.
    `language` = codul limbii interfeței, de exemplu "ro".
    """
    data = {
        "files": files,
        "active": active,
        "width": width,
        "height": height,
        "language": language,
    }
    path = Path(path)
    # Creăm folderul NotepadApp dacă nu există încă
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        # ensure_ascii=False: diacriticele din căi rămân lizibile în fișier
        json.dump(data, f, ensure_ascii=False, indent=2)


def is_positive_int(value):
    """True dacă `value` e un număr întreg mai mare ca 0."""
    # În Python, True/False sunt tot numere întregi, așa că le excludem explicit
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def load_session(path):
    """Citește sesiunea din `path`.

    Returnează un dict cu cheile "files", "active", "width", "height",
    "language", sau None dacă fișierul lipsește, e stricat sau nu are forma așteptată.
    """
    try:
        with Path(path).open("r", encoding="utf-8", newline="") as f:
            data = json.load(f)
    except (OSError, ValueError):
        # OSError: fișierul lipsește sau nu se poate citi.
        # ValueError: nu e JSON valid (sau nu e text UTF-8 valid).
        return None

    # Verificăm că datele au exact forma pe care o scriem noi
    if not isinstance(data, dict):
        return None

    files = data.get("files")
    if not isinstance(files, list):
        return None
    for file in files:
        if not isinstance(file, str):
            return None

    active = data.get("active")
    if active is not None and not isinstance(active, str):
        return None

    width = data.get("width")
    height = data.get("height")
    if not is_positive_int(width) or not is_positive_int(height):
        return None

    # Limba: un session.json vechi n-o are, iar una necunoscută o ignorăm.
    # În ambele cazuri folosim limba implicită, fără să pierdem restul sesiunii.
    language = data.get("language")
    if not isinstance(language, str) or language not in strings.LANGUAGES:
        language = strings.DEFAULT_LANGUAGE

    return {
        "files": files,
        "active": active,
        "width": width,
        "height": height,
        "language": language,
    }

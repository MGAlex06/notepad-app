"""Textele interfeței, în română și engleză.

Folosire: t("menu.open") dă "Deschide..." sau "Open...", după limba curentă.
Textele cu valori variabile au câmpuri numite: t("msg.goto_range", max=10).
"""

# Limbile disponibile și numele lor (numele nu se traduc)
LANGUAGES = {"ro": "Română", "en": "English"}
DEFAULT_LANGUAGE = "ro"

STRINGS = {
    "ro": {
        # Generale
        "app.untitled": "Fără titlu",
        "filetype.text": "Fișiere text",
        "filetype.all": "Toate fișierele",
        "status.chars": "{count} caractere",
        "button.close": "Închide",
        # Mesaje
        "error.title": "Eroare",
        "error.open": "Nu am putut deschide fișierul:\n{error}",
        "error.encode": "Textul conține caractere care nu pot fi salvate în "
                        "{encoding}.\nAlege altă codificare din meniul Codificare.",
        "error.save": "Nu am putut salva fișierul:\n{error}",
        "msg.not_found": 'Nu găsesc "{query}"',
        "msg.replaced": "Am înlocuit {count} potriviri.",
        "msg.goto_range": "Numărul liniei trebuie să fie între 1 și {max}.",
        "msg.save_changes": 'Salvezi modificările din "{name}"?',
        # Ferestrele Caută / Înlocuiește / Salt la linie / Scurtături
        "find.title": "Caută",
        "find.label": "Caută:",
        "find.match_case": "Potrivire majuscule",
        "find.next": "Caută următorul",
        "replace.title": "Înlocuiește",
        "replace.with": "Înlocuiește cu:",
        "replace.one": "Înlocuiește",
        "replace.all": "Înlocuiește tot",
        "goto.title": "Salt la linie",
        "goto.label": "Număr linie:",
        "goto.button": "Salt",
        "shortcuts.title": "Scurtături de la tastatură",
        # Meniuri
        "menu.file": "Fișier",
        "menu.new_tab": "Filă nouă",
        "menu.close_tab": "Închide fila",
        "menu.open": "Deschide...",
        "menu.save": "Salvează",
        "menu.save_as": "Salvează ca...",
        "menu.edit": "Editare",
        "menu.find": "Caută...",
        "menu.replace": "Înlocuiește...",
        "menu.goto": "Salt la linie...",
        "menu.datetime": "Dată și oră",
        "menu.encoding": "Codificare",
        "menu.view": "Vizualizare",
        "menu.word_wrap": "Încadrare text",
        "menu.line_numbers": "Numere de linie",
        "menu.zoom": "Zoom",
        "menu.zoom_in": "Mărește",
        "menu.zoom_out": "Micșorează",
        "menu.zoom_reset": "Dimensiune implicită",
        "menu.help": "Ajutor",
        "menu.shortcuts": "Scurtături de la tastatură...",
        "menu.language": "Limbă / Language",
        # Descrierile din lista de scurtături
        "shortcut.new_tab": "Filă nouă",
        "shortcut.close_tab": "Închide fila",
        "shortcut.open": "Deschide",
        "shortcut.save": "Salvează",
        "shortcut.save_as": "Salvează ca",
        "shortcut.find": "Caută",
        "shortcut.replace": "Înlocuiește",
        "shortcut.goto": "Salt la linie",
        "shortcut.datetime": "Inserează data și ora",
        "shortcut.zoom_in": "Mărește textul",
        "shortcut.zoom_out": "Micșorează textul",
        "shortcut.zoom_reset": "Dimensiune implicită",
        "shortcut.undo": "Anulează",
        "shortcut.redo": "Refă",
        "shortcut.cut": "Taie",
        "shortcut.copy": "Copiază",
        "shortcut.paste": "Lipește",
        "shortcut.select_all": "Selectează tot",
    },
    "en": {
        # General
        "app.untitled": "Untitled",
        "filetype.text": "Text files",
        "filetype.all": "All files",
        "status.chars": "{count} characters",
        "button.close": "Close",
        # Messages
        "error.title": "Error",
        "error.open": "Could not open the file:\n{error}",
        "error.encode": "The text contains characters that cannot be saved in "
                        "{encoding}.\nChoose another encoding from the Encoding menu.",
        "error.save": "Could not save the file:\n{error}",
        "msg.not_found": 'Cannot find "{query}"',
        "msg.replaced": "Replaced {count} matches.",
        "msg.goto_range": "The line number must be between 1 and {max}.",
        "msg.save_changes": 'Save changes to "{name}"?',
        # Find / Replace / Go to line / Shortcuts windows
        "find.title": "Find",
        "find.label": "Find what:",
        "find.match_case": "Match case",
        "find.next": "Find next",
        "replace.title": "Replace",
        "replace.with": "Replace with:",
        "replace.one": "Replace",
        "replace.all": "Replace all",
        "goto.title": "Go to line",
        "goto.label": "Line number:",
        "goto.button": "Go",
        "shortcuts.title": "Keyboard shortcuts",
        # Menus
        "menu.file": "File",
        "menu.new_tab": "New tab",
        "menu.close_tab": "Close tab",
        "menu.open": "Open...",
        "menu.save": "Save",
        "menu.save_as": "Save as...",
        "menu.edit": "Edit",
        "menu.find": "Find...",
        "menu.replace": "Replace...",
        "menu.goto": "Go to line...",
        "menu.datetime": "Date and time",
        "menu.encoding": "Encoding",
        "menu.view": "View",
        "menu.word_wrap": "Word wrap",
        "menu.line_numbers": "Line numbers",
        "menu.zoom": "Zoom",
        "menu.zoom_in": "Zoom in",
        "menu.zoom_out": "Zoom out",
        "menu.zoom_reset": "Restore default size",
        "menu.help": "Help",
        "menu.shortcuts": "Keyboard shortcuts...",
        "menu.language": "Limbă / Language",
        # Shortcut list descriptions
        "shortcut.new_tab": "New tab",
        "shortcut.close_tab": "Close tab",
        "shortcut.open": "Open",
        "shortcut.save": "Save",
        "shortcut.save_as": "Save as",
        "shortcut.find": "Find",
        "shortcut.replace": "Replace",
        "shortcut.goto": "Go to line",
        "shortcut.datetime": "Insert date and time",
        "shortcut.zoom_in": "Zoom in",
        "shortcut.zoom_out": "Zoom out",
        "shortcut.zoom_reset": "Default size",
        "shortcut.undo": "Undo",
        "shortcut.redo": "Redo",
        "shortcut.cut": "Cut",
        "shortcut.copy": "Copy",
        "shortcut.paste": "Paste",
        "shortcut.select_all": "Select all",
    },
}

# Limba curentă; o schimbăm doar prin set_language
_current = DEFAULT_LANGUAGE


def set_language(code):
    """Schimbă limba curentă. Un cod necunoscut dă ValueError (limba rămâne)."""
    global _current
    if code not in STRINGS:
        raise ValueError(f"Limbă necunoscută: {code!r}")
    _current = code


def get_language():
    """Codul limbii curente, de exemplu "ro"."""
    return _current


def t(key, **values):
    """Textul cheii `key` în limba curentă, cu câmpurile {…} completate.

    O cheie fără traducere întoarce chiar cheia (ex. "menu.inexistent"):
    aplicația nu se oprește, iar greșeala se vede imediat pe ecran.
    """
    text = STRINGS[_current].get(key)
    if text is None:
        return key
    return text.format(**values)

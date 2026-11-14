import codecs
import locale
from pathlib import Path

# Pagina de cod "ANSI" a Windows-ului (de ex. cp1252 sau cp1250),
# aceeași pe care o folosește Notepad-ul din Windows.
ANSI_CODEC = locale.getencoding()

# Codificările pe care le știm: numele afișat -> (codec Python, are BOM?)
# BOM-ul e un caracter invizibil ("﻿") pus la începutul fișierului,
# care spune ce codificare are fișierul.
ENCODINGS = {
    "UTF-8": ("utf-8", False),
    "UTF-8 cu BOM": ("utf-8", True),
    "UTF-16 LE": ("utf-16-le", True),
    "UTF-16 BE": ("utf-16-be", True),
    "ANSI": (ANSI_CODEC, False),
}
DEFAULT_ENCODING = "UTF-8"

BOM = "﻿"


def detect_encoding(data):
    """Ghicește codificarea din octeții fișierului și returnează numele ei."""
    # 1. Întâi după BOM (primii octeți ai fișierului)
    if data.startswith(codecs.BOM_UTF8):
        return "UTF-8 cu BOM"
    if data.startswith(codecs.BOM_UTF16_LE):
        return "UTF-16 LE"
    if data.startswith(codecs.BOM_UTF16_BE):
        return "UTF-16 BE"

    # 2. Fără BOM: încercăm UTF-8
    try:
        data.decode("utf-8")
        return "UTF-8"
    except UnicodeDecodeError:
        # 3. Nu e UTF-8 valid: îl tratăm ca ANSI, în loc să dăm eroare
        return "ANSI"


def read_file(path):
    """Citește un fișier text și returnează (text, terminația de linie, codificarea).

    Textul returnat folosește doar "\\n", pentru că zona de text din
    Tkinter lucrează doar cu "\\n". Terminația originală ("\\r\\n" sau "\\n")
    și numele codificării sunt returnate separat, ca să le folosim la salvare.
    """
    # Citim octeții exact cum sunt pe disc (citirea binară nu schimbă
    # terminațiile de linie, la fel ca newline="").
    data = Path(path).read_bytes()
    encoding = detect_encoding(data)
    codec, has_bom = ENCODINGS[encoding]

    # La ANSI, puținii octeți care nu au corespondent devin "�" în loc de eroare
    errors = "replace" if encoding == "ANSI" else "strict"
    content = data.decode(codec, errors=errors)

    if has_bom and content.startswith(BOM):
        content = content[1:]  # BOM-ul nu face parte din text

    if "\r\n" in content:
        newline = "\r\n"
    else:
        newline = "\n"

    text = content.replace("\r\n", "\n")
    return text, newline, encoding


def write_file(path, text, newline="\r\n", encoding=DEFAULT_ENCODING):
    """Scrie textul în fișier, cu terminația de linie și codificarea primite.

    Dacă textul are caractere care nu încap în codificare (de ex. un emoji
    în ANSI), aruncă UnicodeEncodeError fără să atingă fișierul.
    """
    codec, has_bom = ENCODINGS[encoding]

    content = text.replace("\n", newline)
    if has_bom:
        content = BOM + content

    # Verificăm întâi, în memorie, că tot textul se poate codifica.
    # Așa, dacă dă eroare, fișierul de pe disc rămâne neatins.
    content.encode(codec)

    with Path(path).open("w", encoding=codec, newline="") as f:
        f.write(content)

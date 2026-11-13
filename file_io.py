from pathlib import Path


def read_file(path):
    """Citește un fișier text și returnează (text, terminația de linie).

    Textul returnat folosește doar "\\n", pentru că zona de text din
    Tkinter lucrează doar cu "\\n". Terminația originală ("\\r\\n" sau "\\n")
    este returnată separat, ca să o putem folosi la salvare.
    """
    with Path(path).open("r", encoding="utf-8", newline="") as f:
        content = f.read()

    if "\r\n" in content:
        newline = "\r\n"
    else:
        newline = "\n"

    text = content.replace("\r\n", "\n")
    return text, newline


def write_file(path, text, newline="\r\n"):
    """Scrie textul în fișier, folosind terminația de linie primită."""
    content = text.replace("\n", newline)
    with Path(path).open("w", encoding="utf-8", newline="") as f:
        f.write(content)

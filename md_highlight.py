"""Găsește zonele de colorat într-un text Markdown.

Modulul nu știe nimic de Tkinter: primește text și întoarce o listă de zone,
ca să poată fi testat cu pytest. Colorarea propriu-zisă e în document.py.
"""

import re
from collections import namedtuple
from pathlib import Path

# O zonă de colorat. Liniile încep de la 1 (ca în Tkinter), coloanele de la 0.
# Coloanele sunt numărate ca în Python; sfârșitul nu face parte din zonă.
Span = namedtuple("Span", "kind start_line start_col end_line end_col")

# Toate tipurile de zone, în ordinea în care document.py le creează etichetele
KINDS = ["quote", "list", "link", "italic", "bold", "code", "heading", "code_block"]

# Extensiile care pornesc automat modul Markdown
MARKDOWN_SUFFIXES = (".md", ".markdown")

# Titlu: 1-6 caractere # la început de rând, urmate de spațiu sau de capătul rândului
HEADING = re.compile(r"#{1,6}( |$)")
# Citat: > la început de rând (pot fi spații înainte)
QUOTE = re.compile(r"\s*>")
# Element de listă: marcajul - * + sau 1. urmat de spațiu
LIST_ITEM = re.compile(r"\s*([-*+]|\d+\.)\s")
# Stilurile din interiorul unui rând. La aceeași poziție câștigă prima
# alternativă, deci codul inline e verificat primul, iar ** înainte de *.
INLINE = re.compile(
    r"(?P<code>`[^`]+`)"
    r"|(?P<link>\[[^\]]+\]\([^)]+\))"
    r"|(?P<bold>\*\*[^*]+\*\*)"
    # *text* sau _text_; _ nu trebuie să fie lipit de litere (nume_de_variabila)
    r"|(?P<italic>\*[^*\s][^*]*\*|(?<!\w)_[^_\s][^_]*_(?!\w))"
)


def is_fence(line):
    """True dacă rândul deschide sau închide un bloc de cod (```)."""
    return line.lstrip().startswith("```")


def line_spans(number, line):
    """Zonele de pe un singur rând obișnuit (din afara blocurilor de cod)."""
    # Un titlu se colorează în întregime; nu mai căutăm altceva în el
    if HEADING.match(line):
        return [Span("heading", number, 0, number, len(line))]

    spans = []
    inline_start = 0  # de unde căutăm stilurile din interiorul rândului
    if QUOTE.match(line):
        spans.append(Span("quote", number, 0, number, len(line)))
    else:
        marker = LIST_ITEM.match(line)
        if marker:
            # Colorăm doar marcajul (-, *, +, 1.), nu tot rândul
            spans.append(Span("list", number, marker.start(1), number, marker.end(1)))
            inline_start = marker.end()

    for match in INLINE.finditer(line, inline_start):
        # lastgroup = numele alternativei care s-a potrivit (code, link, ...)
        spans.append(Span(match.lastgroup, number, match.start(), number, match.end()))
    return spans


def find_spans(text):
    """Lista zonelor de colorat din `text` (listă goală dacă nu e nimic)."""
    spans = []
    lines = text.split("\n")
    block_start = None  # linia unde a început blocul de cod deschis (None = niciunul)

    for number, line in enumerate(lines, start=1):
        if block_start is not None:
            # Suntem într-un bloc de cod: nu interpretăm nimic, doar căutăm finalul
            if is_fence(line):
                spans.append(Span("code_block", block_start, 0, number, len(line)))
                block_start = None
            continue
        if is_fence(line):
            block_start = number
            continue
        spans.extend(line_spans(number, line))

    # Un bloc neînchis ține până la finalul textului
    if block_start is not None:
        spans.append(Span("code_block", block_start, 0, len(lines), len(lines[-1])))
    return spans


def tk_column(line, column):
    """Transformă o coloană Python în coloana pe care o folosește Tkinter.

    Tkinter 8.6 numără caracterele ca UTF-16: un emoji (ex. 😀) ocupă
    două poziții, deși în Python e un singur caracter. Numărăm deci câte
    unități UTF-16 (câte 2 octeți) are textul dinaintea coloanei.
    """
    return len(line[:column].encode("utf-16-le")) // 2


def is_markdown_path(path):
    """True dacă fișierul are extensia .md sau .markdown (orice litere)."""
    return Path(path).suffix.lower() in MARKDOWN_SUFFIXES

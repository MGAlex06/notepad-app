def find_next(text, query, start, match_case):
    """Caută `query` în `text`, începând de la poziția `start`.

    Returnează poziția (indexul) primei potriviri găsite, sau None dacă
    nu există nicio potrivire de la `start` până la finalul textului.
    Dacă `match_case` este False, literele mari și mici sunt tratate la fel.
    """
    if not query:
        return None

    if not match_case:
        text = text.lower()
        query = query.lower()

    position = text.find(query, start)
    if position == -1:
        return None
    return position


def find_next_wrap(text, query, start, match_case):
    """Ca find_next, dar dacă nu găsește nimic după `start`,
    reia căutarea de la începutul textului.

    Returnează None doar dacă `query` nu apare nicăieri în text.
    """
    position = find_next(text, query, start, match_case)
    if position is None:
        position = find_next(text, query, 0, match_case)
    return position


def is_match_at(text, query, position, match_case):
    """Verifică dacă `query` apare exact la poziția `position` în `text`.

    Returnează True sau False. Un `query` gol nu e niciodată potrivire.
    """
    if not query:
        return False

    piece = text[position:position + len(query)]
    if not match_case:
        piece = piece.lower()
        query = query.lower()
    return piece == query


def replace_all(text, query, replacement, match_case, cursor=0):
    """Înlocuiește toate aparițiile lui `query` din `text` cu `replacement`.

    `cursor` este poziția cursorului (în caractere) în textul vechi.
    Returnează (text_nou, câte_înlocuiri, cursor_nou), unde cursor_nou
    este locul unde ar trebui să ajungă cursorul în textul nou.
    """
    if not query:
        return text, 0, cursor

    pieces = []       # bucățile textului nou, lipite la final
    new_length = 0    # lungimea textului nou construit până acum
    count = 0
    new_cursor = cursor
    start = 0         # de unde căutăm următoarea potrivire

    while True:
        # find_next (nu find_next_wrap): mergem doar înainte, ca bucla să se termine
        position = find_next(text, query, start, match_case)
        if position is None:
            break
        end = position + len(query)

        pieces.append(text[start:position])  # textul dinaintea potrivirii
        pieces.append(replacement)
        new_length += (position - start) + len(replacement)
        count += 1

        if end <= cursor:
            # Potrivirea e înaintea cursorului: cursorul se mută cu diferența de lungime
            new_cursor += len(replacement) - len(query)
        elif position < cursor:
            # Cursorul era în interiorul potrivirii: îl punem după înlocuire
            new_cursor = new_length

        start = end  # continuăm după potrivire, nu în interiorul înlocuirii

    pieces.append(text[start:])  # ce a rămas după ultima potrivire
    return "".join(pieces), count, new_cursor


def parse_line_number(value, line_count):
    """Transformă textul `value` (scris de utilizator) într-un număr de linie.

    `line_count` este câte linii are documentul.
    Returnează numărul liniei (int) dacă e un număr întreg între 1 și
    `line_count`, altfel None.
    """
    try:
        line = int(value.strip())  # " 5 " devine 5; "abc" sau "2.5" dau eroare
    except ValueError:
        return None

    if line < 1 or line > line_count:
        return None
    return line
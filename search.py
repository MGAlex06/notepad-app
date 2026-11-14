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
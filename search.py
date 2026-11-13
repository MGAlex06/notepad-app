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
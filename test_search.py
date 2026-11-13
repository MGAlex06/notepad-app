from search import find_next


def test_finds_first_match():
    assert find_next("Ana are mere", "are", 0, match_case=False) == 4


def test_finds_next_match_after_start():
    text = "mere și mere"
    assert find_next(text, "mere", 1, match_case=False) == 8


def test_returns_none_when_missing():
    assert find_next("Ana are mere", "pere", 0, match_case=False) is None


def test_returns_none_after_last_match():
    assert find_next("mere și mere", "mere", 9, match_case=False) is None


def test_match_case_true_is_strict():
    assert find_next("Ana are mere", "ana", 0, match_case=True) is None


def test_match_case_false_ignores_case():
    assert find_next("Ana are mere", "ana", 0, match_case=False) == 0


def test_diacritics_ignore_case():
    assert find_next("Școala", "ș", 0, match_case=False) == 0


def test_empty_query_returns_none():
    assert find_next("Ana are mere", "", 0, match_case=False) is None
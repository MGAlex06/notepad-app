from search import find_next, find_next_wrap, is_match_at, replace_all


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


def test_wrap_finds_match_after_cursor_without_wrapping():
    assert find_next_wrap("mere și mere", "mere", 1, match_case=False) == 8


def test_wrap_goes_back_to_start_when_nothing_after_cursor():
    assert find_next_wrap("mere și mere", "mere", 9, match_case=False) == 0


def test_wrap_finds_match_that_overlaps_cursor():
    # cursorul e în mijlocul lui "mere" (poziția 10); potrivirea începe la 8
    assert find_next_wrap("Ana are mere", "mere", 10, match_case=False) == 8


def test_wrap_from_end_of_text():
    assert find_next_wrap("Ana are mere", "Ana", 12, match_case=False) == 0


def test_wrap_returns_none_when_missing_everywhere():
    assert find_next_wrap("Ana are mere", "pere", 5, match_case=False) is None


def test_wrap_respects_match_case():
    assert find_next_wrap("Ana are mere", "ana", 5, match_case=True) is None


def test_wrap_empty_query_returns_none():
    assert find_next_wrap("Ana are mere", "", 5, match_case=False) is None


def test_is_match_at_exact():
    assert is_match_at("Ana are mere", "are", 4, match_case=False) is True


def test_is_match_at_wrong_position():
    assert is_match_at("Ana are mere", "are", 3, match_case=False) is False


def test_is_match_at_ignores_case():
    assert is_match_at("Ana are mere", "ANA", 0, match_case=False) is True


def test_is_match_at_respects_case():
    assert is_match_at("Ana are mere", "ana", 0, match_case=True) is False


def test_is_match_at_empty_query():
    assert is_match_at("Ana are mere", "", 0, match_case=False) is False


def test_is_match_at_near_end_does_not_overflow():
    # la poziția 10 au mai rămas doar "re", deci "mere" nu încape
    assert is_match_at("Ana are mere", "mere", 10, match_case=False) is False


def test_replace_all_replaces_and_counts():
    assert replace_all("mere și mere", "mere", "pere", match_case=False) == (
        "pere și pere", 2, 0
    )


def test_replace_all_no_matches():
    assert replace_all("Ana are mere", "pere", "x", match_case=False) == (
        "Ana are mere", 0, 0
    )


def test_replace_all_ignores_case():
    text, count, _ = replace_all("mere Mere MERE", "mere", "pere", match_case=False)
    assert (text, count) == ("pere pere pere", 3)


def test_replace_all_respects_case():
    text, count, _ = replace_all("mere Mere MERE", "mere", "pere", match_case=True)
    assert (text, count) == ("pere Mere MERE", 1)


def test_replace_all_replacement_contains_query():
    # "a" -> "aa" nu trebuie să intre în buclă infinită
    text, count, _ = replace_all("a b a", "a", "aa", match_case=False)
    assert (text, count) == ("aa b aa", 2)


def test_replace_all_with_empty_replacement_deletes():
    text, count, _ = replace_all("a-b-c", "-", "", match_case=False)
    assert (text, count) == ("abc", 2)


def test_replace_all_diacritics():
    text, count, _ = replace_all("Școala și școala", "școala", "casa", match_case=False)
    assert (text, count) == ("casa și casa", 2)


def test_replace_all_empty_query():
    assert replace_all("Ana", "", "x", match_case=False, cursor=2) == ("Ana", 0, 2)


def test_replace_all_cursor_before_matches_unchanged():
    # cursorul la 1, potrivirile sunt după el
    _, _, cursor = replace_all("x mere mere", "mere", "p", match_case=False, cursor=1)
    assert cursor == 1


def test_replace_all_cursor_after_shorter_replacements():
    # "mere mere |x": două înlocuiri cu 3 caractere mai scurte fiecare
    text, _, cursor = replace_all("mere mere x", "mere", "p", match_case=False, cursor=10)
    assert text == "p p x"
    assert cursor == 4
    assert text[cursor] == "x"


def test_replace_all_cursor_after_longer_replacements():
    text, _, cursor = replace_all("a b x", "a", "aaa", match_case=False, cursor=4)
    assert text == "aaa b x"
    assert text[cursor] == "x"


def test_replace_all_cursor_inside_match_goes_after_replacement():
    # cursorul e în mijlocul primului "mere" (poziția 2)
    text, _, cursor = replace_all("mere și mere", "mere", "pere!", match_case=False, cursor=2)
    assert text == "pere! și pere!"
    assert cursor == 5

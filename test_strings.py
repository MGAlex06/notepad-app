import string

import pytest

import strings
from strings import STRINGS, get_language, set_language, t


@pytest.fixture(autouse=True)
def reset_language():
    # Fiecare test pornește în română și o lasă tot așa la final,
    # ca să nu afecteze alte teste (de ex. "Fără titlu" din test_document.py)
    set_language("ro")
    yield
    set_language("ro")


def fields(text):
    """Numele câmpurilor {…} dintr-un text, de ex. {"max"}."""
    return {name for _, name, _, _ in string.Formatter().parse(text) if name}


def test_both_languages_have_same_keys():
    assert STRINGS["ro"].keys() == STRINGS["en"].keys()


def test_both_languages_have_same_fields():
    for key in STRINGS["ro"]:
        assert fields(STRINGS["ro"][key]) == fields(STRINGS["en"][key]), key


def test_languages_list_matches_strings():
    assert strings.LANGUAGES.keys() == STRINGS.keys()
    assert strings.DEFAULT_LANGUAGE in STRINGS


def test_t_follows_set_language():
    set_language("en")
    assert t("menu.file") == "File"
    assert get_language() == "en"

    set_language("ro")
    assert t("menu.file") == "Fișier"
    assert get_language() == "ro"


def test_t_fills_named_fields():
    assert t("msg.goto_range", max=7) == "Numărul liniei trebuie să fie între 1 și 7."
    set_language("en")
    assert t("msg.goto_range", max=7) == "The line number must be between 1 and 7."


def test_unknown_language_is_refused():
    set_language("en")
    with pytest.raises(ValueError):
        set_language("fr")
    assert get_language() == "en"  # limba a rămas cea de dinainte


def test_missing_key_returns_the_key():
    # Alegerea noastră: o cheie fără traducere se afișează ca atare,
    # fără excepție, ca greșeala să se vadă pe ecran
    assert t("cheie.inexistenta") == "cheie.inexistenta"

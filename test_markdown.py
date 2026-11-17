from pathlib import Path

from markdown import Span, find_spans, is_markdown_path, tk_column


def test_plain_text_has_no_spans():
    assert find_spans("Un text obișnuit, fără Markdown.\nAl doilea rând.") == []


def test_empty_text_has_no_spans():
    assert find_spans("") == []


def test_heading_levels_1_to_6():
    for level in range(1, 7):
        line = "#" * level + " Titlu"
        assert find_spans(line) == [Span("heading", 1, 0, 1, len(line))]


def test_seven_hashes_or_no_space_is_not_heading():
    assert find_spans("####### prea multe") == []
    assert find_spans("#eticheta") == []


def test_bold():
    assert find_spans("un **cuvânt** aici") == [Span("bold", 1, 3, 1, 13)]


def test_italic_with_star_and_underscore():
    assert find_spans("un *cuvânt*") == [Span("italic", 1, 3, 1, 11)]
    assert find_spans("un _cuvânt_") == [Span("italic", 1, 3, 1, 11)]


def test_underscore_inside_word_is_not_italic():
    assert find_spans("nume_de_variabila") == []


def test_inline_code_hides_markdown_inside():
    # *x* din interiorul codului nu devine înclinat
    assert find_spans("cod `a *x* b` gata") == [Span("code", 1, 4, 1, 13)]


def test_link():
    assert find_spans("vezi [site](https://example.com)") == [
        Span("link", 1, 5, 1, 32)
    ]


def test_list_markers():
    assert find_spans("- unu") == [Span("list", 1, 0, 1, 1)]
    assert find_spans("* doi") == [Span("list", 1, 0, 1, 1)]
    assert find_spans("+ trei") == [Span("list", 1, 0, 1, 1)]
    assert find_spans("12. patru") == [Span("list", 1, 0, 1, 3)]
    assert find_spans("  - indentat") == [Span("list", 1, 2, 1, 3)]


def test_list_item_with_bold_text():
    assert find_spans("- un **pas**") == [
        Span("list", 1, 0, 1, 1),
        Span("bold", 1, 5, 1, 12),
    ]


def test_quote():
    assert find_spans("> un citat") == [Span("quote", 1, 0, 1, 10)]


def test_code_block_ignores_markdown_inside():
    text = "înainte\n```\n# nu e titlu\n* nici listă **x**\n```\ndupă"
    assert find_spans(text) == [Span("code_block", 2, 0, 5, 3)]


def test_unclosed_code_block_runs_to_end():
    text = "```python\nx = 1 * 2\n# comentariu"
    assert find_spans(text) == [Span("code_block", 1, 0, 3, 12)]


def test_multiple_lines():
    text = "# Titlu\n\ntext cu `cod`\n> citat"
    assert find_spans(text) == [
        Span("heading", 1, 0, 1, 7),
        Span("code", 3, 8, 3, 13),
        Span("quote", 4, 0, 4, 7),
    ]


def test_line_with_emoji_uses_python_columns():
    # 😀 e un singur caracter în Python, deci **b** începe la coloana 2
    assert find_spans("a😀**b**") == [Span("bold", 1, 2, 1, 7)]


def test_tk_column_without_emoji():
    assert tk_column("abc", 2) == 2
    assert tk_column("ăîș", 3) == 3  # diacriticele ocupă tot câte o poziție


def test_tk_column_counts_emoji_as_two():
    line = "a😀**b**"
    assert tk_column(line, 1) == 1  # înainte de emoji
    assert tk_column(line, 2) == 3  # după emoji: +2
    assert tk_column(line, 7) == 8


def test_is_markdown_path():
    assert is_markdown_path("nota.md")
    assert is_markdown_path(Path("C:/doc/README.MD"))
    assert is_markdown_path("ghid.markdown")
    assert not is_markdown_path("nota.txt")
    assert not is_markdown_path("fara_extensie")

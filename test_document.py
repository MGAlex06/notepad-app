import tkinter as tk
from datetime import datetime

import pytest

from document import Document, format_timestamp, gutter_width


@pytest.fixture(scope="module")
def root():
    # O fereastră Tkinter ascunsă, doar ca să putem crea widget-uri în teste.
    # scope="module": o creăm o singură dată pentru tot fișierul, pentru că
    # crearea repetată a mai multor tk.Tk() eșuează uneori pe Windows.
    window = tk.Tk()
    window.withdraw()
    yield window
    window.destroy()


def test_new_document_defaults(root):
    doc = Document(root)
    assert doc.path is None
    assert doc.newline == "\r\n"
    assert doc.encoding.get() == "UTF-8"
    assert doc.display_name() == "Fără titlu"
    assert doc.get_text() == ""


def test_set_word_wrap(root):
    doc = Document(root)

    doc.set_word_wrap(False)
    assert doc.text_area.cget("wrap") == "none"
    assert doc.xscrollbar.winfo_manager() == "pack"  # bara orizontală e afișată

    doc.set_word_wrap(True)
    assert doc.text_area.cget("wrap") == "word"
    assert doc.xscrollbar.winfo_manager() == ""  # bara orizontală e ascunsă


def test_load_reads_text_newline_and_encoding(root, tmp_path):
    path = tmp_path / "nota.txt"
    path.write_bytes(b"\xef\xbb\xbfunu\r\ndoi")  # UTF-8 cu BOM, terminații Windows

    doc = Document(root)
    doc.load(path)

    assert doc.get_text() == "unu\ndoi"
    assert doc.newline == "\r\n"
    assert doc.encoding.get() == "UTF-8 cu BOM"
    assert doc.path == path
    assert doc.display_name() == "nota.txt"


def test_load_clears_undo_history(root, tmp_path):
    path = tmp_path / "nota.txt"
    path.write_bytes(b"continut")

    doc = Document(root)
    doc.text_area.insert("1.0", "ceva scris inainte")
    doc.load(path)

    # Nu mai e nimic de anulat: Tkinter aruncă TclError
    with pytest.raises(tk.TclError):
        doc.text_area.edit_undo()
    assert doc.get_text() == "continut"


def test_load_missing_file_raises_and_keeps_document(root, tmp_path):
    doc = Document(root)
    doc.text_area.insert("1.0", "text vechi")

    with pytest.raises(OSError):
        doc.load(tmp_path / "nu_exista.txt")

    assert doc.get_text() == "text vechi"
    assert doc.path is None


def test_save_uses_newline_and_encoding_and_sets_path(root, tmp_path):
    path = tmp_path / "salvat.txt"

    doc = Document(root)
    doc.text_area.insert("1.0", "a\nb")
    doc.encoding.set("UTF-16 LE")
    doc.save(path)

    assert path.read_bytes() == b"\xff\xfe" + "a\r\nb".encode("utf-16-le")
    assert doc.path == path


def test_new_document_is_blank_and_not_modified(root):
    doc = Document(root)
    assert doc.is_blank()
    assert not doc.is_modified()


def test_typing_marks_document_modified(root):
    doc = Document(root)
    doc.text_area.insert("1.0", "ceva")
    assert doc.is_modified()
    assert not doc.is_blank()


def test_load_clears_modified_flag(root, tmp_path):
    path = tmp_path / "nota.txt"
    path.write_bytes(b"continut")

    doc = Document(root)
    doc.load(path)

    assert not doc.is_modified()
    assert not doc.is_blank()


def test_save_clears_modified_flag(root, tmp_path):
    doc = Document(root)
    doc.text_area.insert("1.0", "ceva")
    doc.save(tmp_path / "salvat.txt")

    assert not doc.is_modified()


def test_save_failure_keeps_path(root, tmp_path):
    doc = Document(root)
    doc.text_area.insert("1.0", "emoji 😀")
    doc.encoding.set("ANSI")

    with pytest.raises(UnicodeEncodeError):
        doc.save(tmp_path / "x.txt")

    assert doc.path is None


def test_gutter_width_grows_with_digits():
    # digit_width=8, padding=4 → lățime = cifre * 8 + 8
    assert gutter_width(0, 8, 4) == 16  # document gol: tot o cifră
    assert gutter_width(1, 8, 4) == 16
    assert gutter_width(9, 8, 4) == 16
    assert gutter_width(10, 8, 4) == 24
    assert gutter_width(99, 8, 4) == 24
    assert gutter_width(100, 8, 4) == 32


def shown_numbers(root, doc):
    """Afișează documentul și întoarce numerele desenate în gutter."""
    # La o fereastră ascunsă Tkinter nu calculează poziția rândurilor,
    # așa că o arătăm pentru o clipă
    doc.frame.pack(fill=tk.BOTH, expand=True)
    root.deiconify()
    try:
        root.update()
        doc.redraw_line_numbers()
        return [doc.gutter.itemcget(item, "text") for item in doc.gutter.find_all()]
    finally:
        root.withdraw()
        doc.frame.destroy()


def test_line_numbers_gutter_shows_each_line(root):
    doc = Document(root)
    doc.text_area.insert("1.0", "a\nb\nc")

    assert doc.gutter.winfo_manager() == "pack"  # gutter-ul există și e afișat
    assert shown_numbers(root, doc) == ["1", "2", "3"]


def test_wrapped_line_gets_one_number(root):
    doc = Document(root)
    doc.text_area.insert("1.0", "cuvant " * 100 + "\nb")  # prima linie se rupe

    assert shown_numbers(root, doc) == ["1", "2"]


def test_set_line_numbers_hides_and_shows(root):
    doc = Document(root)

    doc.set_line_numbers(False)
    assert doc.gutter.winfo_manager() == ""
    assert doc.separator.winfo_manager() == ""

    doc.set_line_numbers(True)
    assert doc.gutter.winfo_manager() == "pack"
    assert doc.separator.winfo_manager() == "pack"


def test_line_numbers_do_not_touch_undo(root, tmp_path):
    path = tmp_path / "nota.txt"
    path.write_bytes(b"unu\r\ndoi")

    doc = Document(root)
    doc.load(path)
    root.update()  # lasă redesenarea programată să ruleze
    doc.redraw_line_numbers()

    assert not doc.is_modified()
    with pytest.raises(tk.TclError):
        doc.text_area.edit_undo()  # nimic de anulat


def test_format_timestamp_fixed_date():
    assert format_timestamp(datetime(2026, 11, 16, 14, 49)) == "14:49 16.11.2026"


def test_format_timestamp_single_digit_time():
    assert format_timestamp(datetime(2026, 11, 16, 9, 5)) == "09:05 16.11.2026"


def test_format_timestamp_single_digit_day_month():
    assert format_timestamp(datetime(2026, 2, 3, 10, 30)) == "10:30 03.02.2026"


def test_format_timestamp_end_of_year():
    assert format_timestamp(datetime(2026, 12, 31, 23, 59)) == "23:59 31.12.2026"

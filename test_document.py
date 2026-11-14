import tkinter as tk

import pytest

from document import Document


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


def test_save_failure_keeps_path(root, tmp_path):
    doc = Document(root)
    doc.text_area.insert("1.0", "emoji 😀")
    doc.encoding.set("ANSI")

    with pytest.raises(UnicodeEncodeError):
        doc.save(tmp_path / "x.txt")

    assert doc.path is None

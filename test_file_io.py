import pytest

from file_io import read_file, write_file


def test_read_diacritics(tmp_path):
    path = tmp_path / "diacritice.txt"
    path.write_bytes("ă î ș ț Ă Î Ș Ț".encode("utf-8"))

    text, newline = read_file(path)

    assert text == "ă î ș ț Ă Î Ș Ț"


def test_read_detects_crlf(tmp_path):
    path = tmp_path / "crlf.txt"
    path.write_bytes(b"linia 1\r\nlinia 2\r\n")

    text, newline = read_file(path)

    assert text == "linia 1\nlinia 2\n"
    assert newline == "\r\n"


def test_read_detects_lf(tmp_path):
    path = tmp_path / "lf.txt"
    path.write_bytes(b"linia 1\nlinia 2\n")

    text, newline = read_file(path)

    assert text == "linia 1\nlinia 2\n"
    assert newline == "\n"


def test_write_crlf(tmp_path):
    path = tmp_path / "out.txt"

    write_file(path, "a\nb\n", "\r\n")

    assert path.read_bytes() == b"a\r\nb\r\n"


def test_write_lf(tmp_path):
    path = tmp_path / "out.txt"

    write_file(path, "a\nb\n", "\n")

    assert path.read_bytes() == b"a\nb\n"


@pytest.mark.parametrize("newline", ["\r\n", "\n"])
def test_write_then_read_roundtrip(tmp_path, newline):
    path = tmp_path / "roundtrip.txt"
    original = "Prima linie cu ă și î\nA doua cu ș și ț\nA treia\n"

    write_file(path, original, newline)
    text, detected = read_file(path)

    assert text == original
    assert detected == newline
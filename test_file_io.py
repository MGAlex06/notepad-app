import pytest

from file_io import ANSI_CODEC, ENCODINGS, detect_encoding, read_file, write_file


def test_read_diacritics(tmp_path):
    path = tmp_path / "diacritice.txt"
    path.write_bytes("ă î ș ț Ă Î Ș Ț".encode("utf-8"))

    text, newline, encoding = read_file(path)

    assert text == "ă î ș ț Ă Î Ș Ț"
    assert encoding == "UTF-8"


def test_read_detects_crlf(tmp_path):
    path = tmp_path / "crlf.txt"
    path.write_bytes(b"linia 1\r\nlinia 2\r\n")

    text, newline, encoding = read_file(path)

    assert text == "linia 1\nlinia 2\n"
    assert newline == "\r\n"


def test_read_detects_lf(tmp_path):
    path = tmp_path / "lf.txt"
    path.write_bytes(b"linia 1\nlinia 2\n")

    text, newline, encoding = read_file(path)

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
    text, detected, encoding = read_file(path)

    assert text == original
    assert detected == newline


# --- Codificări ---


@pytest.mark.parametrize(
    "data, expected",
    [
        (b"\xef\xbb\xbfabc", "UTF-8 cu BOM"),
        (b"\xff\xfea\x00", "UTF-16 LE"),
        (b"\xfe\xff\x00a", "UTF-16 BE"),
        ("ăîșț".encode("utf-8"), "UTF-8"),
        (b"caf\xe9", "ANSI"),  # \xe9 singur nu e UTF-8 valid
        (b"", "UTF-8"),  # fișier gol
    ],
)
def test_detect_encoding(data, expected):
    assert detect_encoding(data) == expected


@pytest.mark.parametrize(
    "data, expected_encoding",
    [
        (b"\xef\xbb\xbfabc", "UTF-8 cu BOM"),
        (b"\xff\xfea\x00b\x00c\x00", "UTF-16 LE"),
        (b"\xfe\xff\x00a\x00b\x00c", "UTF-16 BE"),
    ],
)
def test_read_with_bom_removes_bom(tmp_path, data, expected_encoding):
    path = tmp_path / "bom.txt"
    path.write_bytes(data)

    text, newline, encoding = read_file(path)

    assert text == "abc"
    assert encoding == expected_encoding


def test_read_invalid_utf8_falls_back_to_ansi(tmp_path):
    path = tmp_path / "ansi.txt"
    path.write_bytes(b"caf\xe9")

    text, newline, encoding = read_file(path)

    assert encoding == "ANSI"
    assert text == b"caf\xe9".decode(ANSI_CODEC, errors="replace")


def test_read_detects_crlf_in_utf16(tmp_path):
    path = tmp_path / "utf16.txt"
    path.write_bytes(b"\xff\xfe" + "a\r\nb".encode("utf-16-le"))

    text, newline, encoding = read_file(path)

    assert text == "a\nb"
    assert newline == "\r\n"
    assert encoding == "UTF-16 LE"


@pytest.mark.parametrize(
    "encoding, expected",
    [
        ("UTF-8", b"a\r\n"),
        ("UTF-8 cu BOM", b"\xef\xbb\xbfa\r\n"),
        ("UTF-16 LE", b"\xff\xfea\x00\r\x00\n\x00"),
        ("UTF-16 BE", b"\xfe\xff\x00a\x00\r\x00\n"),
        ("ANSI", b"a\r\n"),
    ],
)
def test_write_encoding_bytes(tmp_path, encoding, expected):
    path = tmp_path / "out.txt"

    write_file(path, "a\n", "\r\n", encoding)

    assert path.read_bytes() == expected


@pytest.mark.parametrize("encoding", list(ENCODINGS))
@pytest.mark.parametrize("newline", ["\r\n", "\n"])
def test_roundtrip_every_encoding(tmp_path, encoding, newline):
    path = tmp_path / "roundtrip.txt"
    if encoding == "ANSI":
        # "é" e scris în ANSI ca un singur octet, care nu e UTF-8 valid,
        # deci la citire fișierul e recunoscut ca ANSI. (Un text doar ASCII
        # ar fi identic în UTF-8 și ar fi detectat ca UTF-8.)
        original = "Café\nA doua linie\n"
    else:
        original = "Cu diacritice: ă î ș ț\nA doua linie\n"

    write_file(path, original, newline, encoding)
    text, detected_newline, detected_encoding = read_file(path)

    assert text == original
    assert detected_newline == newline
    assert detected_encoding == encoding


def test_write_ansi_unencodable_keeps_file(tmp_path):
    path = tmp_path / "ansi.txt"
    path.write_bytes(b"continut vechi")

    with pytest.raises(UnicodeEncodeError):
        write_file(path, "emoji 😀", "\r\n", "ANSI")

    assert path.read_bytes() == b"continut vechi"

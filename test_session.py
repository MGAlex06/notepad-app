import pytest

from session import load_session, save_session


def test_save_then_load_roundtrip(tmp_path):
    path = tmp_path / "session.json"
    files = [r"C:\Documente\notițe.txt", r"C:\Documente\listă.txt"]

    save_session(path, files, r"C:\Documente\listă.txt", 1024, 768, "en")

    assert load_session(path) == {
        "files": files,
        "active": r"C:\Documente\listă.txt",
        "width": 1024,
        "height": 768,
        "language": "en",
    }


def test_roundtrip_without_active_file(tmp_path):
    path = tmp_path / "session.json"

    save_session(path, [], None, 800, 600, "ro")

    assert load_session(path) == {
        "files": [],
        "active": None,
        "width": 800,
        "height": 600,
        "language": "ro",
    }


def test_save_creates_folder(tmp_path):
    path = tmp_path / "NotepadApp" / "session.json"

    save_session(path, [], None, 800, 600, "ro")

    assert path.is_file()


def test_load_missing_file_returns_none(tmp_path):
    assert load_session(tmp_path / "nu_exista.json") is None


def test_load_broken_json_returns_none(tmp_path):
    path = tmp_path / "session.json"
    path.write_text("{ nu e json", encoding="utf-8")

    assert load_session(path) is None


def test_load_invalid_utf8_returns_none(tmp_path):
    path = tmp_path / "session.json"
    path.write_bytes(b"\xff\xfe\x00")

    assert load_session(path) is None


@pytest.mark.parametrize(
    "content",
    [
        '["nu", "e", "dict"]',
        '{"files": "a.txt", "active": null, "width": 800, "height": 600}',
        '{"files": [1, 2], "active": null, "width": 800, "height": 600}',
        '{"files": [], "active": 5, "width": 800, "height": 600}',
        '{"files": [], "active": null, "width": -5, "height": 600}',
        '{"files": [], "active": null, "width": "800", "height": 600}',
        '{"files": [], "active": null, "width": true, "height": 600}',
        '{"files": [], "active": null, "width": 800}',
        "{}",
    ],
)
def test_load_wrong_shape_returns_none(tmp_path, content):
    path = tmp_path / "session.json"
    path.write_text(content, encoding="utf-8")

    assert load_session(path) is None


def test_old_session_without_language_uses_romanian(tmp_path):
    # Un session.json scris înainte să existe alegerea limbii
    path = tmp_path / "session.json"
    path.write_text(
        '{"files": ["a.txt"], "active": null, "width": 800, "height": 600}',
        encoding="utf-8",
    )

    data = load_session(path)

    assert data["language"] == "ro"
    assert data["files"] == ["a.txt"]  # restul sesiunii se încarcă normal


@pytest.mark.parametrize("language", ['"fr"', "5", "null", '["en"]'])
def test_unknown_language_falls_back_to_romanian(tmp_path, language):
    path = tmp_path / "session.json"
    path.write_text(
        '{"files": ["a.txt"], "active": null, "width": 800, "height": 600, '
        f'"language": {language}}}',
        encoding="utf-8",
    )

    data = load_session(path)

    assert data["language"] == "ro"
    assert data["files"] == ["a.txt"]

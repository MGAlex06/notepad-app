import pytest

from session import load_session, save_session


def test_save_then_load_roundtrip(tmp_path):
    path = tmp_path / "session.json"
    files = [r"C:\Documente\notițe.txt", r"C:\Documente\listă.txt"]

    save_session(path, files, r"C:\Documente\listă.txt", 1024, 768)

    assert load_session(path) == {
        "files": files,
        "active": r"C:\Documente\listă.txt",
        "width": 1024,
        "height": 768,
    }


def test_roundtrip_without_active_file(tmp_path):
    path = tmp_path / "session.json"

    save_session(path, [], None, 800, 600)

    assert load_session(path) == {
        "files": [],
        "active": None,
        "width": 800,
        "height": 600,
    }


def test_save_creates_folder(tmp_path):
    path = tmp_path / "NotepadApp" / "session.json"

    save_session(path, [], None, 800, 600)

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

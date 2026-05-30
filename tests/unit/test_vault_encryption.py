"""The secure vault must encrypt file contents at rest, not move plaintext."""

from security.content_management import ContentCategory, ContentManager, SecurityLevel

_SECRET = b"SECRET: a private journal page"


def _vault(tmp_path):
    return ContentManager(tmp_path)


def test_hidden_folder_encrypts_contents(tmp_path):
    cm = _vault(tmp_path)
    folder = cm.create_secure_folder(
        "private", ContentCategory.SENSITIVE, SecurityLevel.HIGH, "pw", hide_folder=True
    )
    src = tmp_path / "page.txt"
    src.write_bytes(_SECRET)

    assert cm.move_to_secure_folder(src, folder.name, "pw") is True
    assert not src.exists(), "the plaintext original must be removed"

    enc = folder / "page.txt.enc"
    assert enc.exists(), "an encrypted blob must be written"
    assert _SECRET not in enc.read_bytes(), "stored bytes must not be plaintext"


def test_extract_round_trips_and_rejects_wrong_passcode(tmp_path):
    cm = _vault(tmp_path)
    folder = cm.create_secure_folder(
        "private", ContentCategory.SENSITIVE, SecurityLevel.HIGH, "pw", hide_folder=True
    )
    src = tmp_path / "page.txt"
    src.write_bytes(_SECRET)
    cm.move_to_secure_folder(src, folder.name, "pw")

    out = tmp_path / "out.txt"
    assert cm.extract_from_secure_folder(folder.name, "pw", "page.txt", out) is True
    assert out.read_bytes() == _SECRET

    assert cm.extract_from_secure_folder(folder.name, "wrong", "page.txt", out) is False


def test_wrong_passcode_blocks_move(tmp_path):
    cm = _vault(tmp_path)
    folder = cm.create_secure_folder(
        "private", ContentCategory.SENSITIVE, SecurityLevel.HIGH, "pw", hide_folder=True
    )
    src = tmp_path / "page.txt"
    src.write_bytes(_SECRET)
    assert cm.move_to_secure_folder(src, folder.name, "nope") is False
    assert src.exists(), "a failed access check must not consume the file"

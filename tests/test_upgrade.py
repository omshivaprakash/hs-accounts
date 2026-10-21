import io
import tarfile

import pytest

from expense_ledger import utils


def make_tar(files):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for name, content in files.items():
            info = tarfile.TarInfo(name)
            info.size = len(content)
            tar.addfile(info, io.BytesIO(content))
    return buf.getvalue()


GOOD = {
    "owner-repo-abc1234/apps/expense_ledger/pyproject.toml": b"[project]",
    "owner-repo-abc1234/apps/expense_ledger/expense_ledger/hooks.py": b"app_name = 'x'",
    "owner-repo-abc1234/ingestion/bot.py": b"not part of the app",
}


def test_extracts_only_the_app(tmp_path):
    root = utils.extract_app(make_tar(GOOD), str(tmp_path))
    assert (tmp_path / "apps/expense_ledger/expense_ledger/hooks.py").exists()
    assert not (tmp_path / "ingestion").exists()
    assert root.endswith("apps/expense_ledger/")


def test_rejects_path_traversal(tmp_path):
    evil = {**GOOD, "owner-repo-abc1234/apps/expense_ledger/../../../escape.txt": b"x"}
    with pytest.raises(ValueError, match="unsafe"):
        utils.extract_app(make_tar(evil), str(tmp_path / "out"))
    assert not (tmp_path / "escape.txt").exists()


def test_rejects_archive_without_the_app(tmp_path):
    with pytest.raises(ValueError, match="does not contain"):
        utils.extract_app(make_tar({"o-r-1/README.md": b"hi"}), str(tmp_path))


def test_valid_source():
    assert utils.valid_source("omshivaprakash/hs-accounts", "main")
    assert utils.valid_source("a/b", "release/1.0")
    for repo, branch in [("evil.com/../x/y", "main"), ("a/b", "../x"), ("a/b", "m ain"), ("ab", "main"), ("", "main")]:
        assert not utils.valid_source(repo, branch)

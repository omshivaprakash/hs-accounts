import json
import re
from pathlib import Path

from expense_ledger import utils

ROOT = Path(__file__).resolve().parent.parent
DOCS = sorted((ROOT / "apps/expense_ledger/expense_ledger/docs").glob("*.md"))


def test_doc_title():
    assert utils.doc_title("intro\n# Real Title\nbody") == "Real Title"
    assert utils.doc_title("no heading") == "Untitled"


def test_every_help_topic_is_well_formed_and_listed_in_the_readme():
    assert DOCS, "no help topics found"
    readme = (ROOT / "README.md").read_text()
    titles = []
    for p in DOCS:
        assert re.fullmatch(r"\d\d-[a-z0-9-]+\.md", p.name), p.name  # numeric prefix sets the order
        title = utils.doc_title(p.read_text())
        assert title != "Untitled", p.name
        assert p.name in readme, f"{p.name} is not linked from the README"
        titles.append(title)
    assert len(set(titles)) == len(titles)


def test_help_page_definition_matches_its_folder():
    page = ROOT / "apps/expense_ledger/expense_ledger/expense_ledger/page/expense_ledger_help"
    meta = json.loads((page / "expense_ledger_help.json").read_text())
    assert meta["name"] == meta["page_name"] == "expense-ledger-help"
    assert 'frappe.pages["expense-ledger-help"]' in (page / "expense_ledger_help.js").read_text()

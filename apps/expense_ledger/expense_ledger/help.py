"""Serves the markdown in expense_ledger/docs to the Help page in the desk."""
import os

import frappe
from frappe import _
from frappe.utils import md_to_html

from expense_ledger import utils

DOCS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")


def _names():
    return sorted(f[:-3] for f in os.listdir(DOCS) if f.endswith(".md"))


def _read(name):
    with open(os.path.join(DOCS, name + ".md"), encoding="utf-8") as fh:
        return fh.read()


@frappe.whitelist()
def topics():
    return [{"name": n, "title": utils.doc_title(_read(n))} for n in _names()]


@frappe.whitelist()
def topic(name):
    if name not in _names():  # only our own files: the name never reaches the filesystem otherwise
        frappe.throw(_("Unknown help topic"))
    return md_to_html(_read(name))

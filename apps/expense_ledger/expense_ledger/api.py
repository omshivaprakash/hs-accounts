"""Whitelisted actions behind the list-view buttons: batch claims, mark paid, Tally export."""
import os
from urllib.parse import quote

import frappe
import requests
from frappe import _
from frappe.utils import get_first_day, get_last_day, getdate

from expense_ledger import tally_xml, utils

PERSONAL_MODES = ("Personal Card", "Personal UPI")
MANAGERS = ("System Manager", "Accounts Manager")
USERS = MANAGERS + ("Accounts User",)
INGEST_URL = os.environ.get("INGEST_URL", "http://watcher:8090/ingest")  # the ingestion service, see ingestion/server.py
CARD = ["name", "vendor", "invoice_no", "bill_date", "grand_total", "paid_by", "payment_mode", "expense_category", "needs_review", "docstatus"]


@frappe.whitelist()
def create_claims(month, category=None):
    """Draft one claim per payee (and category, when given) for the month's unclaimed personal payments."""
    frappe.only_for(MANAGERS)
    first = get_first_day(month)
    filters = {
        "docstatus": 1,
        "disposition": "Business",
        "payment_mode": ["in", PERSONAL_MODES],
        "claim": ["is", "not set"],
        "paid_by": ["is", "set"],
        "bill_date": ["between", [first, get_last_day(first)]],
    }
    if category:
        filters["expense_category"] = category
    bills = frappe.get_all("Bill", filters=filters, fields=["name", "paid_by", "expense_category"])
    made = []
    for (payee, cat), rows in utils.claim_groups(bills, by_category=bool(category)).items():
        doc = frappe.get_doc(
            {"doctype": "Reimbursement Claim", "payee": payee, "period": first, "category": cat, "bills": [{"bill": r["name"]} for r in rows]}
        ).insert()
        made.append(doc.name)
    return made


@frappe.whitelist()
def mark_paid(names, paid_on, reference=None):
    """Record payment on approved reimbursement claims. Saved through the document so it lands in the audit trail."""
    frappe.only_for(MANAGERS)
    done = 0
    for name in frappe.parse_json(names):
        claim = frappe.get_doc("Reimbursement Claim", name)
        if claim.docstatus == 1 and claim.settlement == "Reimburse" and claim.payment_status == "Unpaid":
            claim.payment_status, claim.paid_on, claim.payment_reference = "Paid", getdate(paid_on), reference
            claim.save()
            done += 1
    return done


@frappe.whitelist()
def export_tally(from_date, to_date, kind="Vouchers", entity=None):
    frappe.only_for(MANAGERS + ("Expense Accountant",))
    s = frappe.get_single("Expense Ledger Settings")
    if not s.tally_company:
        frappe.throw(_("Set the Tally company name in Expense Ledger Settings first"))
    filters = {"docstatus": 1, "disposition": "Business", "bill_date": ["between", [from_date, to_date]]}
    if entity:
        filters["entity"] = entity
    bills = frappe.get_all(
        "Bill",
        filters=filters,
        fields=["name", "vendor", "invoice_no", "bill_date", "expense_category", "cgst", "sgst", "igst", "grand_total", "paid_by", "payment_mode"],
        order_by="bill_date, name",
    )
    cats = {c.name: (c.tally_ledger or c.name, c.is_capex) for c in frappe.get_all("Expense Category", fields=["name", "tally_ledger", "is_capex"])}
    gst = {
        "cgst": s.input_cgst_ledger or "Input CGST",
        "sgst": s.input_sgst_ledger or "Input SGST",
        "igst": s.input_igst_ledger or "Input IGST",
    }
    build = tally_xml.masters_xml if kind.startswith("Ledger") else tally_xml.vouchers_xml
    frappe.response.filename = f"tally-{'masters' if kind.startswith('Ledger') else 'vouchers'}-{from_date}-to-{to_date}.xml"
    frappe.response.filecontent = build(bills, cats, s.tally_company, gst).encode("utf-8")
    frappe.response.type = "download"


def _card(name, **extra):
    card = frappe.db.get_value("Bill", name, CARD, as_dict=True)
    card.can_confirm = bool(set(frappe.get_roles()) & set(MANAGERS))
    card.update(extra)
    return card


@frappe.whitelist(methods=["POST"])
def drop_bill():
    """One dropped invoice or receipt: OCR it, create the draft Bill, default Paid By to the uploader."""
    frappe.only_for(USERS)
    f = frappe.request.files.get("file")
    if not f:
        frappe.throw(_("No file received"))
    try:
        r = requests.post(INGEST_URL, data=f.stream.read(), headers={"X-Filename": quote(f.filename or "")}, timeout=180)
    except requests.RequestException:
        frappe.throw(_("The reader service is not running. Ask an administrator to start it."))
    if not r.ok:
        frappe.throw(_(r.json().get("error", "Could not read this file")))
    res = r.json()
    if res["duplicate"]:
        return _card(res["name"], duplicate=True)
    payee = frappe.db.get_value("Payee", {"user": frappe.session.user})
    if payee:
        frappe.db.set_value("Bill", res["name"], "paid_by", payee)
    return _card(res["name"], duplicate=False, missing=res["missing"])


@frappe.whitelist(methods=["POST"])
def update_bill(name, payment_mode=None, paid_by=None, expense_category=None, confirm=0):
    """Fill the three things OCR cannot know and optionally confirm (submit needs Accounts Manager)."""
    frappe.only_for(USERS)
    doc = frappe.get_doc("Bill", name)
    if doc.docstatus != 0:
        frappe.throw(_("{0} is already confirmed").format(name))
    doc.update({k: v for k, v in dict(payment_mode=payment_mode, paid_by=paid_by, expense_category=expense_category).items() if v})
    doc.save()
    if int(confirm):
        doc.submit()
    return _card(name)

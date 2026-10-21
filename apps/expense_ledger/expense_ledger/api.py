"""Whitelisted actions behind the list-view buttons: batch claims, mark paid, Tally export."""
import frappe
from frappe import _
from frappe.utils import get_first_day, get_last_day, getdate

from expense_ledger import tally_xml, utils

PERSONAL_MODES = ("Personal Card", "Personal UPI")
MANAGERS = ("System Manager", "Accounts Manager")


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

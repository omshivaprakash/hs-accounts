import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, get_first_day, getdate, nowdate

from expense_ledger import utils

PERSONAL_MODES = ("Personal Card", "Personal UPI")
BILL_FIELDS = ["docstatus", "payment_mode", "paid_by", "claim", "bill_date", "vendor", "invoice_no", "expense_category", "grand_total"]


class ReimbursementClaim(Document):
    def validate(self):
        if not self.bills:
            frappe.throw(_("Add at least one bill"))
        seen = set()
        for row in self.bills:
            if row.bill in seen:
                frappe.throw(_("Row {0}: {1} is listed twice").format(row.idx, row.bill))
            seen.add(row.bill)
            b = frappe.db.get_value("Bill", row.bill, BILL_FIELDS, as_dict=True)
            if not b or b.docstatus != 1:
                frappe.throw(_("{0} is not a confirmed bill").format(row.bill))
            if b.payment_mode not in PERSONAL_MODES:
                frappe.throw(_("{0} was not paid personally, so it cannot be claimed").format(row.bill))
            if b.paid_by != self.payee:
                frappe.throw(_("{0} was paid by {1}, not {2}").format(row.bill, b.paid_by, self.payee))
            if b.claim and b.claim != self.name:
                frappe.throw(_("{0} is already in claim {1}").format(row.bill, b.claim))
            row.update({k: b[k] for k in ("bill_date", "vendor", "invoice_no", "expense_category")})
            row.amount = b.grand_total  # the full amount the person paid, tax included
        self.total = flt(sum(r.amount for r in self.bills), 2)
        self.period = get_first_day(self.period)
        self.financial_year = utils.financial_year(getdate(self.period))
        if self.settlement == "Capital Contribution":
            self.payment_status = "Not Applicable"
        elif self.payment_status in (None, "", "Not Applicable"):
            self.payment_status = "Unpaid"

    def on_update(self):
        # reserve the bills so they cannot land in a second claim
        names = [r.bill for r in self.bills]
        for n in names:
            frappe.db.set_value("Bill", n, "claim", self.name, update_modified=False)
        for stale in frappe.get_all("Bill", {"claim": self.name, "name": ["not in", names]}, pluck="name"):
            frappe.db.set_value("Bill", stale, "claim", None, update_modified=False)

    def before_submit(self):
        # Submitting is the approval; Accounts Manager holds the submit permission
        self.approved_by = frappe.session.user

    def on_submit(self):
        if self.settlement != "Capital Contribution":
            return
        cc = frappe.get_doc(
            {
                "doctype": "Capital Contribution",
                "contributor": self.payee,
                "contributed_on": nowdate(),
                "amount": self.total,
                "claim": self.name,
                "reference": f"Unreimbursed claim {self.name}",
            }
        ).insert(ignore_permissions=True)
        cc.submit()
        self.db_set("capital_contribution", cc.name)

    def on_cancel(self):
        self.release_bills()
        if self.capital_contribution:
            cc = frappe.get_doc("Capital Contribution", self.capital_contribution)
            if cc.docstatus == 1:
                cc.cancel()

    def on_trash(self):
        self.release_bills()

    def release_bills(self):
        for n in frappe.get_all("Bill", {"claim": self.name}, pluck="name"):
            frappe.db.set_value("Bill", n, "claim", None, update_modified=False)

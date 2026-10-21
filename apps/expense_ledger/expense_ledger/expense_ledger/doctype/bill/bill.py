import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate

from expense_ledger import utils

REQUIRED_TO_CONFIRM = ("vendor", "invoice_no", "bill_date", "grand_total", "expense_category", "payment_mode", "paid_by")


class Bill(Document):
    def validate(self):
        self.financial_year = utils.financial_year(getdate(self.bill_date)) if self.bill_date else None
        self.net_amount, self.total_tax, self.grand_total, consistent = utils.totals(
            self.net_amount, self.cgst, self.sgst, self.igst, self.grand_total
        )
        if not consistent:
            self.needs_review = 1
        if self.vendor and not self.expense_category:
            self.suggest_classification()
        self.warn_if_duplicate()

    def suggest_classification(self):
        rules = frappe.get_all("Vendor Category Rule", fields=["vendor_pattern", "expense_category", "cost_center"])
        rule = utils.match_rule(self.vendor, rules)
        if rule:
            self.expense_category = rule["expense_category"]
            self.cost_center = self.cost_center or rule["cost_center"]

    def warn_if_duplicate(self):
        if not (self.vendor and self.invoice_no):
            return
        dup = frappe.db.exists(
            "Bill",
            {"vendor": self.vendor, "invoice_no": self.invoice_no, "docstatus": ["<", 2], "name": ["!=", self.name]},
        )
        if dup:
            self.needs_review = 1
            frappe.msgprint(_("Possible duplicate of {0}").format(dup), indicator="orange")

    def before_submit(self):
        # Submitting is the human "tick": nothing is confirmed until a person does it.
        missing = [self.meta.get_label(f) for f in REQUIRED_TO_CONFIRM if not self.get(f)]
        if missing:
            frappe.throw(_("Cannot confirm. Missing: {0}").format(", ".join(missing)))
        if self.disposition in ("Spam", "Trash"):
            frappe.throw(_("A bill marked {0} cannot be confirmed").format(self.disposition))
        self.disposition = "Business"
        self.needs_review = 0

    def on_submit(self):
        self.learn_rule()

    def learn_rule(self):
        pattern = self.vendor.strip().lower()
        rule = frappe.get_doc("Vendor Category Rule", pattern) if frappe.db.exists("Vendor Category Rule", pattern) else frappe.new_doc("Vendor Category Rule")
        rule.update(vendor_pattern=pattern, expense_category=self.expense_category, cost_center=self.cost_center)
        rule.hits = (rule.hits or 0) + 1
        rule.save(ignore_permissions=True)

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class PettyCashWithdrawal(Document):
    def validate(self):
        self.spent = 0 if self.is_new() else flt(
            frappe.db.sql("select coalesce(sum(grand_total), 0) from `tabBill` where petty_cash = %s and docstatus = 1", self.name)[0][0], 2
        )
        self.balance = flt(self.amount - self.spent, 2)
        if self.balance < 0:
            frappe.throw(_("Confirmed spends ({0}) exceed the withdrawal ({1})").format(self.spent, self.amount))

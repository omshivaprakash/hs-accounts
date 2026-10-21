import frappe
from frappe import _
from frappe.model.document import Document

import expense_ledger
from expense_ledger import utils


class ExpenseLedgerSettings(Document):
    def onload(self):
        self.installed_version = expense_ledger.__version__

    def validate(self):
        if not utils.valid_source(self.github_repo, self.branch):
            frappe.throw(_("Repository must look like owner/repo and the branch must be a plain branch name"))

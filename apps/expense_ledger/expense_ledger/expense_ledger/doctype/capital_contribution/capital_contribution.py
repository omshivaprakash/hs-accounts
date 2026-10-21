from frappe.model.document import Document
from frappe.utils import getdate

from expense_ledger import utils


class CapitalContribution(Document):
    def validate(self):
        self.financial_year = utils.financial_year(getdate(self.contributed_on))

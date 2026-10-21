import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate

from expense_ledger import utils


class Capitalization(Document):
    """Gathers what went into a built product or IP and turns it into an ERPNext Asset.

    Capitalization rule (proposed default, still open): a record can be submitted only once the product is
    ready AND deployed to a location. The deployment date becomes the asset's available-for-use date.
    """

    def validate(self):
        self.company = self.company or frappe.defaults.get_global_default("company")
        total = 0
        for row in self.costs:
            if row.bill:
                b = frappe.db.get_value("Bill", row.bill, ["docstatus", "capitalization", "net_amount", "vendor"], as_dict=True)
                if not b or b.docstatus != 1:
                    frappe.throw(_("Row {0}: {1} is not a confirmed bill").format(row.idx, row.bill))
                if b.capitalization and b.capitalization != self.name:
                    frappe.throw(_("Row {0}: {1} is already capitalized in {2}").format(row.idx, row.bill, b.capitalization))
                # taxable value by default: recoverable GST is not part of the asset's cost; edit the row if that differs
                row.amount = flt(row.amount) or flt(b.net_amount)
                row.description = row.description or b.vendor
            elif not row.description:
                frappe.throw(_("Row {0}: describe cost lines that have no bill (for example in-house labour)").format(row.idx))
            total += flt(row.amount)
        self.total_cost = flt(total, 2)
        self.financial_year = utils.financial_year(getdate(self.deployed_on)) if self.deployed_on else None

    def before_submit(self):
        missing = [self.meta.get_label(f) for f in ("company", "asset_category", "location", "ready_on", "deployed_on") if not self.get(f)]
        if missing:
            frappe.throw(_("Cannot capitalize yet. Needs: {0}").format(", ".join(missing)))
        if getdate(self.deployed_on) < getdate(self.ready_on):
            frappe.throw(_("Deployment cannot be before the product was ready"))
        if self.total_cost <= 0:
            frappe.throw(_("Add the costs that went into this {0}").format(self.kind))

    def on_submit(self):
        for row in self.costs:
            if row.bill:
                frappe.db.set_value("Bill", row.bill, "capitalization", self.name, update_modified=False)
        self.db_set("asset", self.create_asset())

    def create_asset(self):
        item = f"{self.kind} - {self.title}"[:140]
        if not frappe.db.exists("Item", item):
            frappe.get_doc(
                {
                    "doctype": "Item",
                    "item_code": item,
                    "item_name": self.title,
                    "item_group": "All Item Groups",
                    "stock_uom": "Nos",
                    "is_stock_item": 0,
                    "is_fixed_asset": 1,
                    "asset_category": self.asset_category,
                }
            ).insert(ignore_permissions=True)
        asset = frappe.get_doc(
            {
                "doctype": "Asset",
                "asset_name": self.title,
                "item_code": item,
                "company": self.company,
                "asset_category": self.asset_category,
                "location": self.location,
                "cost_center": self.cost_center,
                "gross_purchase_amount": self.total_cost,
                "purchase_date": self.ready_on,
                "available_for_use_date": self.deployed_on,
                "is_existing_asset": 1,  # cost is already incurred; no purchase receipt or invoice to link
                "calculate_depreciation": 0,
                "asset_owner": "Company",
                "capitalization": self.name,
            }
        ).insert(ignore_permissions=True)
        asset.submit()
        return asset.name

    def on_cancel(self):
        if self.asset:
            asset = frappe.get_doc("Asset", self.asset)
            if asset.docstatus == 1:
                asset.cancel()
        for n in frappe.get_all("Bill", {"capitalization": self.name}, pluck="name"):
            frappe.db.set_value("Bill", n, "capitalization", None, update_modified=False)

import frappe
from frappe import _

# (fieldname, label, fieldtype, width, options)
COLUMNS = [
    ("name", "Bill", "Link", 130, "Bill"),
    ("bill_date", "Invoice Date", "Date", 100, None),
    ("invoice_no", "Invoice No", "Data", 130, None),
    ("vendor", "Vendor", "Data", 180, None),
    ("vendor_gstin", "Vendor GSTIN", "Data", 150, None),
    ("expense_category", "Category", "Link", 140, "Expense Category"),
    ("net_amount", "Taxable Value", "Currency", 120, None),
    ("cgst", "CGST", "Currency", 100, None),
    ("sgst", "SGST", "Currency", 100, None),
    ("igst", "IGST", "Currency", 100, None),
    ("total_tax", "Total Tax", "Currency", 100, None),
    ("grand_total", "Invoice Total", "Currency", 120, None),
    ("payment_mode", "Payment Mode", "Data", 120, None),
    ("paid_by", "Paid By", "Data", 110, None),
    ("tds_flag", "TDS May Apply", "Check", 90, None),
    ("tds_amount", "TDS Amount", "Currency", 100, None),
    ("financial_year", "FY", "Data", 80, None),
]


def execute(filters=None):
    f = frappe._dict(filters or {})
    cond = {"docstatus": 1, "bill_date": ["between", [f.from_date, f.to_date]]}
    if f.entity:
        cond["entity"] = f.entity
    rows = frappe.get_all("Bill", filters=cond, fields=[c[0] for c in COLUMNS], order_by="bill_date, invoice_no")
    columns = [
        {"fieldname": n, "label": _(label), "fieldtype": t, "width": w, **({"options": o} if o else {})}
        for n, label, t, w, o in COLUMNS
    ]
    return columns, rows

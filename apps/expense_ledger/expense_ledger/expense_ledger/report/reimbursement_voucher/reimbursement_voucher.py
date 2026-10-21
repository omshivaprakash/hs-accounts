import frappe
from frappe import _

COLUMNS = [
    ("claim", "Claim", "Link", 130, "Reimbursement Claim"),
    ("payee", "Payee", "Link", 130, "Payee"),
    ("period", "Month", "Date", 90, None),
    ("bill_date", "Bill Date", "Date", 100, None),
    ("vendor", "Vendor", "Data", 180, None),
    ("invoice_no", "Invoice No", "Data", 130, None),
    ("expense_category", "Category", "Link", 140, "Expense Category"),
    ("amount", "Amount", "Currency", 110, None),
    ("settlement", "Settlement", "Data", 130, None),
    ("payment_status", "Payment", "Data", 100, None),
]


def execute(filters=None):
    f = frappe._dict(filters or {})
    # SQL rather than get_all so the child rows come with their claim; the report is limited to managers and the accountant
    rows = frappe.db.sql(
        """
        select c.name claim, c.payee, c.period, b.bill_date, b.vendor, b.invoice_no, b.expense_category,
               b.amount, c.settlement, c.payment_status
        from `tabReimbursement Claim` c join `tabClaim Bill` b on b.parent = c.name
        where c.docstatus = 1 and c.period between %(from_date)s and %(to_date)s
          and (%(payee)s = '' or c.payee = %(payee)s)
        order by c.payee, c.period, b.bill_date
        """,
        {"from_date": f.from_date, "to_date": f.to_date, "payee": f.payee or ""},
        as_dict=True,
    )
    columns = [
        {"fieldname": n, "label": _(label), "fieldtype": t, "width": w, **({"options": o} if o else {})}
        for n, label, t, w, o in COLUMNS
    ]
    return columns, rows

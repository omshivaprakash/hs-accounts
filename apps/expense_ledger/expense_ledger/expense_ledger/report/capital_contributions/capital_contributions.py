import frappe
from frappe import _

COLUMNS = [
    ("name", "Contribution", "Link", 140, "Capital Contribution"),
    ("contributor", "Contributor", "Link", 140, "Payee"),
    ("contributed_on", "Date", "Date", 100, None),
    ("financial_year", "FY", "Data", 80, None),
    ("amount", "Amount", "Currency", 120, None),
    ("claim", "From Claim", "Data", 140, None),
    ("reference", "Reference", "Data", 220, None),
]


def execute(filters=None):
    f = frappe._dict(filters or {})
    rows = frappe.db.sql(
        """
        select name, contributor, contributed_on, financial_year, amount, claim, reference
        from `tabCapital Contribution`
        where docstatus = 1
          and (%(fy)s = '' or financial_year = %(fy)s)
          and (%(who)s = '' or contributor = %(who)s)
        order by contributed_on, name
        """,
        {"fy": f.financial_year or "", "who": f.contributor or ""},
        as_dict=True,
    )
    columns = [
        {"fieldname": n, "label": _(label), "fieldtype": t, "width": w, **({"options": o} if o else {})}
        for n, label, t, w, o in COLUMNS
    ]
    return columns, rows

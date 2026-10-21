import frappe
from frappe import _

COLUMNS = [
    ("expense_category", "Category", "Link", 160, "Expense Category"),
    ("cost_center", "Cost Center", "Link", 160, "Cost Center"),
    ("bills", "Bills", "Int", 70, None),
    ("net_amount", "Taxable Value", "Currency", 120, None),
    ("total_tax", "Tax", "Currency", 100, None),
    ("grand_total", "Total", "Currency", 120, None),
]


def execute(filters=None):
    f = frappe._dict(filters or {})
    rows = frappe.db.sql(
        """
        select expense_category, cost_center, count(*) bills,
               sum(net_amount) net_amount, sum(total_tax) total_tax, sum(grand_total) grand_total
        from `tabBill`
        where docstatus = 1 and bill_date between %(from_date)s and %(to_date)s
        group by expense_category, cost_center
        order by grand_total desc
        """,
        {"from_date": f.from_date, "to_date": f.to_date},
        as_dict=True,
    )
    columns = [
        {"fieldname": n, "label": _(label), "fieldtype": t, "width": w, **({"options": o} if o else {})}
        for n, label, t, w, o in COLUMNS
    ]
    return columns, rows

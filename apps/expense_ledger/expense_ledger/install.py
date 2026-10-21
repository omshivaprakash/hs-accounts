import frappe

# (name, is_capex, tds_possible). Draft list from the brief, still to be finalised.
CATEGORIES = [
    ("R&D Materials", 0, 0),
    ("Equipment Repair", 0, 0),
    ("Utilities", 0, 0),
    ("Housekeeping", 0, 1),
    ("Rent", 0, 1),
    ("Travel", 0, 0),
    ("Meals and Meetings", 0, 0),
    ("Fuel", 0, 0),
    ("Delivery", 0, 0),
    ("Software/SaaS", 0, 0),
    ("Professional Fees", 0, 1),
    ("Capex Item", 1, 0),
]


def after_install():
    for name, is_capex, tds in CATEGORIES:
        if not frappe.db.exists("Expense Category", name):
            frappe.get_doc(
                {"doctype": "Expense Category", "category_name": name, "is_capex": is_capex, "tds_possible": tds}
            ).insert(ignore_permissions=True)


def make_api_keys(user="Administrator"):
    """Run via `bench execute`; prints env lines for the ingestion service."""
    from frappe.core.doctype.user.user import generate_keys

    secret = generate_keys(user)["api_secret"]
    frappe.db.commit()
    print(f"FRAPPE_API_KEY={frappe.db.get_value('User', user, 'api_key')}")
    print(f"FRAPPE_API_SECRET={secret}")

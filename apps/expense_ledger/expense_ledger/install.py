import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

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


def create_roles():
    """Runs before the doctypes sync because their permissions refer to this role."""
    if not frappe.db.exists("Role", "Expense Accountant"):
        frappe.get_doc({"doctype": "Role", "role_name": "Expense Accountant", "desk_access": 1}).insert(ignore_permissions=True)


def after_install():
    setup()


def setup():
    """Idempotent: runs on install and from the migrate patch, so existing sites get new seed data too."""
    create_roles()
    for name, is_capex, tds in CATEGORIES:
        if not frappe.db.exists("Expense Category", name):
            frappe.get_doc(
                {"doctype": "Expense Category", "category_name": name, "is_capex": is_capex, "tds_possible": tds}
            ).insert(ignore_permissions=True)
    if not frappe.db.exists("Payee", "Company"):
        frappe.get_doc({"doctype": "Payee", "payee_name": "Company", "kind": "Company"}).insert(ignore_permissions=True)
    # Data, not Link: a Link would stop the Capitalization being cancelled while its asset points back at it
    create_custom_fields(
        {"Asset": [{"fieldname": "capitalization", "label": "Capitalization Record", "fieldtype": "Data", "read_only": 1, "insert_after": "asset_name"}]}
    )


def make_api_keys(user="Administrator"):
    """Run via `bench execute`; prints env lines for the ingestion service."""
    from frappe.core.doctype.user.user import generate_keys

    secret = generate_keys(user)["api_secret"]
    frappe.db.commit()
    print(f"FRAPPE_API_KEY={frappe.db.get_value('User', user, 'api_key')}")
    print(f"FRAPPE_API_SECRET={secret}")

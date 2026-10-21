"""Claimants see only their own claims and contributions; managers and the accountant see everything.

A Payee is linked to a login through its `user` field, so onboarding a claimant is: create the user,
create the Payee, link them.
"""
import frappe

PRIVILEGED = {"System Manager", "Accounts Manager", "Expense Accountant"}


def _privileged(user):
    return bool(PRIVILEGED & set(frappe.get_roles(user)))


def _conditions(table, field, user):
    user = user or frappe.session.user
    if _privileged(user):
        return ""
    return f"`tab{table}`.`{field}` in (select name from `tabPayee` where `user` = {frappe.db.escape(user)})"


def _allowed(field, doc, user):
    user = user or frappe.session.user
    payee = doc.get(field)
    return _privileged(user) or bool(payee and frappe.db.get_value("Payee", payee, "user") == user)


def claim_conditions(user=None):
    return _conditions("Reimbursement Claim", "payee", user)


def contribution_conditions(user=None):
    return _conditions("Capital Contribution", "contributor", user)


def claim_has_permission(doc, ptype=None, user=None):
    return None if _allowed("payee", doc, user) else False


def contribution_has_permission(doc, ptype=None, user=None):
    return None if _allowed("contributor", doc, user) else False

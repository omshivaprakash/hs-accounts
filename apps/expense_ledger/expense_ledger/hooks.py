app_name = "expense_ledger"
app_title = "Expense Ledger"
app_publisher = "HG Accounts"
app_description = "Bill capture, classification, reimbursements, GST register, Tally export and asset capitalization on ERPNext"

required_apps = ["erpnext"]

before_install = "expense_ledger.install.create_roles"
after_install = "expense_ledger.install.after_install"

permission_query_conditions = {
    "Reimbursement Claim": "expense_ledger.permissions.claim_conditions",
    "Capital Contribution": "expense_ledger.permissions.contribution_conditions",
}
has_permission = {
    "Reimbursement Claim": "expense_ledger.permissions.claim_has_permission",
    "Capital Contribution": "expense_ledger.permissions.contribution_has_permission",
}

app_name = "expense_ledger"
app_title = "Expense Ledger"
app_publisher = "HG Accounts"
app_description = "Bill capture, classification and GST purchase register on ERPNext"

required_apps = ["erpnext"]

after_install = "expense_ledger.install.after_install"

# Getting started

Expense Ledger turns the bills your team pays into confirmed, categorised records, works out who is owed money, and produces the GST register and Tally files your accountant needs. The **Expense Ledger** workspace in the sidebar is the dashboard and the starting point for everything.

## The routine

- **Every day or two:** new bills arrive (drop folder, Telegram, or entered by hand). Review each one and confirm it. See *Bills*.
- **Once a month:** draft the reimbursement claims, approve them, pay people, and mark them paid. See *Claims and reimbursements*.
- **When it happens:** record petty cash withdrawals, capital contributions, and finished products or IP that should become assets.
- **At period end:** run the GST Purchase Register and export to Tally. See *Reports and Tally*.

## One-time setup (administrator)

1. Finish ERPNext's setup wizard (company, financial year). Cost centers do not exist until a company does.
2. Open **Expense Category** and review the starter list. Mark which categories are capital items and which may attract TDS, and give each a Tally ledger name if it differs from the category name.
3. Create a **Payee** for everyone who pays or funds on the company's behalf, including a person who infuses capital. A payee called "Company" already exists for company-direct payments.
4. Open **Expense Ledger Settings** and fill in the Tally company name and your GST ledger names.
5. Create user logins and give them roles (below). Link each claimant's login to their Payee so they can see their own claims.

## Roles

- **Accounts User:** enters and edits bills and claims, sees only their own claims and contributions.
- **Accounts Manager:** confirms bills, approves and pays claims, confirms contributions and capitalizations.
- **Expense Accountant:** read and export only. Meant for the person who keeps the books in Tally.
- **System Manager:** everything, including Settings and upgrades.

Every change to a bill, claim or contribution is kept in the document's version history (the timeline at the bottom of the form).

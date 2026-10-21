# Reports and Tally

All reports count confirmed records only: confirmed bills, approved claims, confirmed contributions.

## Reports

- **GST Purchase Register:** confirmed business bills in a date range, with vendor GSTIN, taxable value, CGST, SGST, IGST, invoice total, payment details and the TDS flag and amount. Export to Excel from the report menu for filing or reconciliation. Filter by entity if you track more than one.
- **Expenses by Category:** totals by category and cost center for a date range.
- **Reimbursement Voucher:** claim lines by payee and month.
- **Capital Contributions:** contributions by financial year and contributor.
- **Asset Register:** ERPNext's own report of capitalized assets.

## Exporting to Tally

The accountant never has to open this system. Send them these files.

1. In **Expense Ledger Settings**, fill in the Tally company name exactly as Tally spells it, and the names of your input CGST, SGST and IGST ledgers.
2. Give an Expense Category a **Tally Ledger** if Tally calls it something different. Otherwise the category name is used.
3. Open the Bills list and choose **Export to Tally**. Pick the date range.
4. Download **Ledger masters** first. In Tally, import it with Import Data, Masters. Vendors become Sundry Creditors, categories become Indirect Expenses (capital items go under Fixed Assets) and the GST ledgers go under Duties and Taxes.
5. Download **Vouchers** for the same range and import it. Each confirmed bill becomes a purchase voucher: the voucher number is the bill number, the reference is the vendor's invoice number, and the narration says who paid and how.

Do not import the same range twice, or Tally will see duplicates. This layout is a first version; if your accountant prefers a different template, tell your administrator.

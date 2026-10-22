# Bills

A **Bill** is one invoice or receipt. It starts as a draft, and **submitting it confirms it**. Nothing counts in reports, claims or Tally until it is confirmed.

## How bills arrive

- **Drop a Bill (easiest):** open **Drop a Bill** from the Expense Ledger home. Drag in one or more invoices or receipts, or click to choose files or take a photo on a phone. Each file is read at once and shows the vendor, date and total. Pick who paid, how it was paid and the category, then **Save**. A manager can press **Confirm** straight away. If a card says *Check the details*, open the full form and correct it first.
- **Drop folder:** put PDFs or photos in the `inbox` folder on the machine running the system. Each file is read, a draft bill is created, and the file moves to `inbox/processed`. Files that could not be read move to `inbox/failed`. Nothing is ever deleted.
- **Telegram:** send a PDF or photo to the bot. It replies with what it found and three buttons: **Business**, **Spam**, **Trash**. Only chats on the allowed list are served.
- **By hand:** open the Bills list and choose New.

The same file is never ingested twice. The original is always attached to the bill under *Source Document*.

## Reviewing a bill

Open the draft and check the details against the attached original. A bill marked **Needs Review** has at least one of these: the text could not be read confidently, the vendor, invoice number, date or total is missing, the taxable value plus tax does not match the total, or the same vendor and invoice number already exist.

Fill in or correct:

- Vendor, invoice number, bill date and the amounts: taxable value, CGST, SGST or IGST, and the invoice total.
- **Payment Mode** and **Paid By**. Corporate Card, Personal Card, Personal UPI, Bank Transfer or Petty Cash. Pick the payee who actually paid.
- **Expense Category** and **Cost Center**. If the vendor has been seen before, these are pre-filled.
- **Entity** if you track more than one.
- **TDS Amount** if the bill is flagged *TDS May Apply*.
- For Petty Cash, the withdrawal it was paid from.

## Confirming

Choose **Submit**. It will refuse until vendor, invoice number, date, total, category, payment mode and paid by are all filled in, and it will refuse a bill marked Spam or Trash. Confirming also teaches the system: next time that vendor appears, its category and cost center are suggested.

You cannot edit a confirmed bill. To change one, cancel it and amend it. A bill that is already in a claim, a capitalization or a Tally export you have sent needs that sorted out first.

## Spam and trash

The Telegram buttons, or the **Disposition** field, mark a bill as Business, Spam or Trash. Spam and Trash bills cannot be confirmed and are left out of the dashboard counts. Business only records your intent; the bill still needs to be submitted.

## Rules

**Vendor Category Rule** holds what the system has learned. Each rule matches part of a vendor name and gives a category and cost center. You can edit or delete rules, and add your own.

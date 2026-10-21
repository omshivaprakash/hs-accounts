# Expense Ledger (Phase 1)

Bill capture, classification and a GST purchase register, built as a small Frappe app on top of ERPNext. No accounting engine of its own.

```
apps/expense_ledger/   Frappe app: Bill, Expense Category, Vendor Category Rule, GST Purchase Register report
ingestion/             OCR + parser, inbox watcher, Telegram bot (talks to Frappe over REST)
docker-compose.yml     Local stack: ERPNext + app + watcher + bot
tests/                 Parser, helpers, ingest pipeline
```

## Run locally

Needs Docker with Compose v2.

1. `scripts/dev.sh up` and wait a few minutes. First start builds the image and creates the site. Watch with `scripts/dev.sh logs create-site`.
2. Open http://localhost:8080, log in as `Administrator` / `admin` (set in `.env`), and finish the ERPNext setup wizard. A Company is needed before Cost Centers exist.
3. `scripts/dev.sh keys` writes an API key and secret to `.env` (it uses Administrator; swap in a dedicated user later).
4. `scripts/dev.sh ingest` starts the folder watcher. Drop PDFs or images into `inbox/`. They move to `inbox/processed/` or `inbox/failed/` and are never deleted.
5. Optional Telegram: create a bot with @BotFather, put the token and your chat ids in `.env`, then `scripts/dev.sh bot`. Send a bill to the bot; tap Business, Spam or Trash on the reply. Chats not in `TELEGRAM_ALLOWED_CHAT_IDS` are ignored.

After editing the app, `scripts/dev.sh up` rebuilds, then `scripts/dev.sh migrate`.

Tests: `pip install pytest && pytest`.

## How a bill flows

1. File arrives (folder or Telegram). A SHA-256 of the file stops the same file being ingested twice.
2. Digital PDFs use their text layer; scans and photos go through tesseract. Low OCR confidence, a missing vendor, invoice number, date or total, or net + tax not matching the total sets **Needs Review**.
3. A Draft **Bill** is created with the original attached. If the vendor matches a **Vendor Category Rule**, the category and cost center are pre-filled.
4. A person fills Payment Mode and Paid By, checks the rest, and **submits**. Submit is the confirmation: it fails if required fields are empty, and it teaches the vendor rule for next time.
5. **GST Purchase Register** (Accounting > Reports) lists confirmed bills for a date range with GSTIN, taxable value, CGST/SGST/IGST and TDS flag, exportable to Excel.

Every edit to a Bill is tracked in its version history.

## Built vs deferred

Built: ingestion (folder, Telegram), OCR, classification with learning, payer/payment mode/entity capture, duplicate warnings, FY tagging, TDS flag, GST register, audit trail.

Not built yet, on purpose: email ingestion, line items, reimbursement and capital-contribution workflow, petty cash, approvals by month, Tally export, asset/IP capitalization, the private limited entity. Roles use ERPNext's Accounts User (enter) and Accounts Manager (confirm) for now.

## Open items from the brief

Final category list and cost-center structure (the 12 seeded categories are a draft in `install.py`), email ingestion yes/no, capitalization trigger, GST on inter-entity rent and support charges, who approves claims, hosting target, Tally template from the accountant.

# Expense Ledger

Bill capture, classification, reimbursements, a GST purchase register, Tally export and asset capitalization, built as a small Frappe app on top of ERPNext. No accounting engine of its own.

```
apps/expense_ledger/   Frappe app: bills, claims, petty cash, capital contributions, capitalizations, reports, Tally export
ingestion/             OCR + parser, inbox watcher, Telegram bot (talks to Frappe over REST)
docker-compose.yml     Local stack: ERPNext + app + watcher + bot
tests/                 Parser, helpers, ingest pipeline, Tally export, upgrade safety, help docs
```

## Run locally

Needs Docker with Compose v2.

1. `scripts/dev.sh up` and wait a few minutes. First start builds the image and creates the site. Watch with `scripts/dev.sh logs create-site`.
2. Open http://localhost:8080, log in as `Administrator` / `admin` (set in `.env`), and finish the ERPNext setup wizard. A Company is needed before Cost Centers exist.
3. `scripts/dev.sh keys` writes an API key and secret to `.env` (it uses Administrator; swap in a dedicated user later).
4. `scripts/dev.sh ingest` starts the folder watcher. Drop PDFs or images into `inbox/`. They move to `inbox/processed/` or `inbox/failed/` and are never deleted.
5. Optional Telegram: create a bot with @BotFather, put the token and your chat ids in `.env`, then `scripts/dev.sh bot`. Send a bill to the bot; tap Business, Spam or Trash on the reply. Chats not in `TELEGRAM_ALLOWED_CHAT_IDS` are ignored.

## Dashboard and upgrades

Open **Expense Ledger** in the sidebar for the dashboard: counts of bills needing review, drafts to confirm, confirmed bills and spend, spend charts by month and category, and shortcuts to the register, categories, rules, the ERPNext accounting documents (journal, payment, purchase invoice, chart of accounts, cost centers, assets) and admin (company, users, settings).

To upgrade: **Expense Ledger Settings** (System Manager only) > *Check for updates*, then *Upgrade now*. It downloads the latest commit of the configured GitHub repo and branch, overlays the app code, and runs `bench migrate`. Then run `scripts/dev.sh restart` so the running services load the new Python code. A private repo needs a read-only token in the same page. Use this page, not an image rebuild, to update a running system: the app code now sits in the `app-code` volume, which a rebuilt image does not overwrite. To start over from the image, `docker compose down`, remove the `*_app-code` volume (`docker volume ls`), then `scripts/dev.sh up`.

Editing the app locally still works the same way: copy the changes into the running site with the upgrade page after pushing, or reset the volume as above.

Tests: `pip install pytest && pytest`.

## How a bill flows

1. File arrives (folder or Telegram). A SHA-256 of the file stops the same file being ingested twice.
2. Digital PDFs use their text layer; scans and photos go through tesseract. Low OCR confidence, a missing vendor, invoice number, date or total, or net + tax not matching the total sets **Needs Review**.
3. A Draft **Bill** is created with the original attached. If the vendor matches a **Vendor Category Rule**, the category and cost center are pre-filled.
4. A person fills Payment Mode and Paid By, checks the rest, and **submits**. Submit is the confirmation: it fails if required fields are empty, and it teaches the vendor rule for next time.
5. **GST Purchase Register** (Accounting > Reports) lists confirmed bills for a date range with GSTIN, taxable value, CGST/SGST/IGST and TDS flag, exportable to Excel.

Every edit to a Bill is tracked in its version history.

## Reimbursements, petty cash and Tally (Phase 2)

- **Payee** is anyone who pays or funds: claimants, fund providers, and "Company". Link a Payee to a user login and that user sees only their own claims and contributions. Bills now record **Paid By** as a Payee.
- **Reimbursement Claim**: in the claims list, *Create Claims* drafts one claim per payee for a month's confirmed personal-card and UPI bills, optionally for one category. Bills are reserved so none lands in two claims. Approve by filtering the list (month, payee) and using the list's bulk **Submit**; submitting is the approval and needs Accounts Manager. *Mark Paid* then records the date and reference on the selected approved claims.
- **Settlement**: a claim can instead be set to *Capital Contribution*. Approving it then creates the payee's capital contribution rather than a payment.
- **Petty Cash Withdrawal** records a bank-to-cash withdrawal. Bills paid by *Petty Cash* pick the withdrawal, cannot exceed its balance, and keep its spent and balance current.
- **Export to Tally** (Bills list): downloads Tally XML for confirmed bills in a date range, as purchase vouchers, plus a ledger-masters file to import first. Set the Tally company and GST ledger names in Settings, and optionally a Tally ledger per Expense Category. The accountant's exact template is still open, so treat this as a first cut.
- Reports: *Reimbursement Voucher* (by payee and month), *Expenses by Category*, plus the GST register.

Roles: Accounts User enters bills and claims, Accounts Manager approves and pays, the new **Expense Accountant** role is read and export only, System Manager administers.

## Capital contributions and assets (Phase 3)

- **Capital Contribution** records money a person puts in, tagged to the financial year. Draft by anyone allowed, confirmed by Accounts Manager submitting it. Contributions from approved claims are created and confirmed automatically. The *Capital Contributions* report totals them by year and person.
- **Capitalization** gathers what went into a built product or IP: confirmed bills (raw materials, parts) plus free-form cost lines for in-house labour, with a narrative and an optional attached document. Submitting it creates and submits an ERPNext **Asset** for the total cost, linked back to the record, and marks the bills as capitalized so they cannot be used twice. Cancelling it cancels the asset and frees the bills.
- **Capitalization rule (proposed default, still open):** a record can be submitted only once the product is ready and deployed to a location. The deployment date becomes the asset's available-for-use date. Costs default to each bill's taxable value because recoverable GST is not part of an asset's cost; edit the row if that is wrong for a bill.
- The asset is created as an existing asset with no depreciation schedule. Set up the Asset Category (and an intangible one for IP) and Locations in ERPNext first.

## Help and documentation

The help is built into the system: open **Expense Ledger** in the sidebar and choose **Help**, then pick a topic from the dropdown. The topics are plain Markdown in `apps/expense_ledger/expense_ledger/docs/`. They ship with the app, so the in-app upgrade updates the help too, and the numeric file prefix sets their order. Edit them like any other file and they appear in the Help page after the next upgrade or restart.

- [Getting started](apps/expense_ledger/expense_ledger/docs/01-getting-started.md): the routine, one-time setup and roles
- [Bills](apps/expense_ledger/expense_ledger/docs/02-bills.md): how bills arrive, review and confirmation
- [Claims and reimbursements](apps/expense_ledger/expense_ledger/docs/03-claims-and-reimbursements.md): monthly claims, approval and payment
- [Petty cash](apps/expense_ledger/expense_ledger/docs/04-petty-cash.md): withdrawals and spending from them
- [Capital contributions and assets](apps/expense_ledger/expense_ledger/docs/05-capital-and-assets.md): contributions and capitalizing built products or IP
- [Reports and Tally](apps/expense_ledger/expense_ledger/docs/06-reports-and-tally.md): the reports and the Tally export steps
- [Administration](apps/expense_ledger/expense_ledger/docs/07-administration.md): people, settings, upgrades and backups
- [Troubleshooting](apps/expense_ledger/expense_ledger/docs/08-troubleshooting.md): common problems and fixes

## Built vs deferred

Built: Phases 1 to 3 above, the dashboard and in-app upgrade.

Not built yet, on purpose: email ingestion, line items on bills, bank statement reconciliation, depreciation setup for assets, the private limited entity (Phase 4).

## Open items from the brief

Final category list and cost-center structure (the 12 seeded categories are a draft in `install.py`), email ingestion yes/no, whether the ready-and-deployed capitalization rule is the one you want, GST on inter-entity rent and support charges, who approves claims and contributions (Accounts Manager today), hosting target, Tally template from the accountant.

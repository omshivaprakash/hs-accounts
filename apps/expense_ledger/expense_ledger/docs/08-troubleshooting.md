# Troubleshooting

## Bills are not appearing

- **Dropped files:** check the watcher is running (`scripts/dev.sh ingest`) and look in `inbox/failed` and `scripts/dev.sh logs watcher`. If the log says it cannot reach Frappe, it retries on its own once the site is up.
- **Nothing is created and the log mentions authorisation:** the API keys are missing or old. Run `scripts/dev.sh keys`, then start the watcher again.
- **Telegram does not answer:** your chat id must be in `TELEGRAM_ALLOWED_CHAT_IDS`, and the bot must be running (`scripts/dev.sh bot`).
- **Message says already ingested:** that exact file was seen before. Open the bill it names.

## A bill will not confirm

The message lists the empty fields. Fill them in and submit again. A bill marked Spam or Trash cannot be confirmed; set its disposition back to Pending or Business first. A petty cash bill also needs the withdrawal and enough balance.

## A bill cannot be cancelled

It is in a claim or a capitalization. Cancel or remove it there first.

## Create Claims made nothing

See the list at the end of *Claims and reimbursements*. Most often the bills are still drafts or have no Paid By.

## A capitalization will not submit

It needs the company, asset category, location, ready date and deployment date, a deployment date that is not before the ready date, and costs above zero. If the asset itself fails, ERPNext is usually missing an Asset Category setup or a Location; the message names the field.

## Tally export asks for a company

Fill in the Tally company name in Expense Ledger Settings.

## An upgrade failed

Read the log on the Settings page. A 404 on a private repository means a token is needed. A failed database update means the code is already new; fix the cause, run the upgrade again, then restart the services.

## Low OCR confidence

Photos of crumpled printed bills are the weakest case. They are flagged for review on purpose, so check the amounts against the original. Digital PDFs are far more reliable.

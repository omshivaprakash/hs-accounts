# Administration

## People

- **Add a user** the usual ERPNext way, and give them Accounts User, Accounts Manager or Expense Accountant.
- **Onboard a claimant or fund provider:** create a Payee for them, choose the kind, and link their login. Without a linked login a payee can still be paid and claimed for, but cannot sign in to see their own claims.
- A person who has left can simply stop being used. Existing bills and claims keep their payee.

## Categories and rules

Edit **Expense Category** to change the list, mark capital items, flag TDS, and set Tally ledger names. Edit **Vendor Category Rule** to correct anything the system learned wrongly.

## Settings

**Expense Ledger Settings** (System Manager only) holds the Tally details and the upgrade source.

## Upgrading

1. Open Expense Ledger Settings and choose **Check for updates**. It compares the installed commit with the latest on the configured repository and branch.
2. Choose **Upgrade now**. It downloads the latest code, applies it, and runs the database update. Follow the status and log on the same page.
3. When it says Done, restart the services so they load the new code: run `scripts/dev.sh restart` on the machine hosting the system.

A private repository needs a read-only access token in Settings. If an upgrade fails, the log says why. Fix the cause and run it again; the code may already have been updated, which is fine.

## Backups

The database, the uploaded bill files and the app code each live in a Docker volume. To take a backup with files, run `docker compose exec backend bench --site frontend backup --with-files` on the host. The backup lands in the site's backups folder inside the sites volume; copy it somewhere else regularly. The original bills in `inbox/processed`, `inbox/failed` and `inbox/telegram` are also kept on the host.

## Security notes

Change the default administrator and database passwords before putting this on a shared network. The Telegram bot answers only the chats listed in `TELEGRAM_ALLOWED_CHAT_IDS`.

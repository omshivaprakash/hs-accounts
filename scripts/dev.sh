#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f .env ] || cp .env.example .env
dc() { docker compose "$@"; }

case "${1:-}" in
  up)      dc up -d --build ;;
  keys)
    keys=$(dc exec -T backend bench --site frontend execute expense_ledger.install.make_api_keys | grep '^FRAPPE_API_') \
      || { echo "key generation failed; is the site up? (scripts/dev.sh logs create-site)"; exit 1; }
    { grep -v '^FRAPPE_API_' .env || true; echo "$keys"; } > .env.new && mv .env.new .env
    echo "API keys written to .env" ;;
  ingest)  dc up -d --build watcher ;;
  bot)     dc up -d --build bot ;;
  migrate) dc exec backend bench --site frontend migrate ;;
  logs)    dc logs -f --tail=100 "${@:2}" ;;
  down)    dc --profile ingest --profile telegram down ;;
  *)       echo "usage: $0 up | keys | ingest | bot | migrate | logs [service] | down"; exit 1 ;;
esac

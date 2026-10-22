#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f .env ] || cp .env.example .env
dc() { docker compose "$@"; }

case "${1:-}" in
  up)
    dc build backend
    mkdir -p data/db data/logs data/sites
    # an empty bind mount would hide the sites/ (assets, config) baked into the image, so seed it once
    [ -e data/sites/apps.txt ] || docker run --rm --user root -v "$PWD/data/sites:/dest" expense-ledger-frappe \
      bash -c 'cp -a sites/. /dest/ && chown -R 1000:1000 /dest /dest/.. 2>/dev/null; chown -R 1000:1000 /dest'
    mkdir -p data/logs && chown -R 1000:1000 data/logs 2>/dev/null || true
    dc up -d --build
    # first run: wait for the site, make the API keys, then start the reader (watcher) with them
    grep -q '^FRAPPE_API_KEY=.' .env || for i in $(seq 60); do "$0" keys 2>/dev/null && break; echo "waiting for the site ($i/60)..."; sleep 15; done
    dc up -d watcher ;;
  keys)
    keys=$(dc exec -T backend bench --site frontend execute expense_ledger.install.make_api_keys | grep '^FRAPPE_API_') \
      || { echo "key generation failed; is the site up? (scripts/dev.sh logs create-site)"; exit 1; }
    { grep -v '^FRAPPE_API_' .env || true; echo "$keys"; } > .env.new && mv .env.new .env
    echo "API keys written to .env" ;;
  ingest)  dc up -d --build watcher ;;
  bot)     dc up -d --build bot ;;
  migrate) dc exec backend bench --site frontend migrate ;;
  restart) dc restart backend queue scheduler ;;
  logs)    dc logs -f --tail=100 "${@:2}" ;;
  down)    dc --profile ingest --profile telegram down ;;
  *)       echo "usage: $0 up | keys | ingest | bot | migrate | restart | logs [service] | down"; exit 1 ;;
esac

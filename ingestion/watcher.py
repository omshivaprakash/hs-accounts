"""Polls the inbox folder and ingests new bills. Files move to processed/ or failed/, never deleted."""
import shutil
import time

import requests

from . import pipeline, telegram
from .client import Frappe

EXT = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}


def _move(p, folder):
    dest = pipeline.INBOX / folder
    dest.mkdir(exist_ok=True)
    target = dest / p.name
    if target.exists():
        target = dest / f"{p.stem}-{int(time.time())}{p.suffix}"
    shutil.move(str(p), str(target))


def scan(client):
    for p in sorted(pipeline.INBOX.iterdir()):
        if not p.is_file() or p.suffix.lower() not in EXT or time.time() - p.stat().st_mtime < 3:
            continue  # skip files still being copied in
        try:
            res = pipeline.ingest(client, p, "Drop Folder")
        except requests.ConnectionError:
            print("Frappe unreachable, will retry", flush=True)
            return
        except Exception as e:
            print(f"failed {p.name}: {e}", flush=True)
            _move(p, "failed")
            continue
        _move(p, "processed")
        telegram.notify(pipeline.summary(res), None if res["duplicate"] else res["name"])


def main():
    client = Frappe.from_env()
    pipeline.INBOX.mkdir(exist_ok=True)
    print(f"watching {pipeline.INBOX.resolve()}", flush=True)
    while True:
        scan(client)
        time.sleep(10)


if __name__ == "__main__":
    main()

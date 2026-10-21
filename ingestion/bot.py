"""Telegram bot: send a bill (PDF or photo) to ingest it; tap Business/Spam/Trash to mark it."""
import sys
import time
from pathlib import Path

import requests

from . import pipeline, telegram
from .client import Frappe

EXT = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}


def handle_callback(client, q):
    msg = q["message"]
    if msg["chat"]["id"] not in telegram.ALLOWED:
        return
    action, _, bill = q["data"].partition(":")
    if action not in telegram.ACTIONS:
        return
    client.set_disposition(bill, action)
    telegram.api("answerCallbackQuery", callback_query_id=q["id"], text=f"{bill}: {action}")
    telegram.api("editMessageReplyMarkup", chat_id=msg["chat"]["id"], message_id=msg["message_id"], reply_markup={"inline_keyboard": []})


def handle_message(client, m):
    chat = m["chat"]["id"]
    if chat not in telegram.ALLOWED:
        return
    doc = m.get("document") or (m.get("photo") or [None])[-1]
    if not doc:
        return
    info = telegram.api("getFile", file_id=doc["file_id"])
    suffix = Path(info["file_path"]).suffix.lower()
    if suffix not in EXT:
        telegram.api("sendMessage", chat_id=chat, text="Send a PDF or an image.")
        return
    r = requests.get(f"https://api.telegram.org/file/bot{telegram.TOKEN}/{info['file_path']}", timeout=60)
    if not r.ok:
        raise RuntimeError(f"telegram download: {r.status_code}")
    dest = pipeline.INBOX / "telegram"
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / f"{doc['file_unique_id']}{suffix}"
    path.write_bytes(r.content)  # original stays on disk for audit
    res = pipeline.ingest(client, path, "Telegram")
    extra = {} if res["duplicate"] else {"reply_markup": telegram.keyboard(res["name"])}
    telegram.api("sendMessage", chat_id=chat, text=pipeline.summary(res), **extra)


def main():
    if not (telegram.TOKEN and telegram.ALLOWED):
        sys.exit("Set TELEGRAM_BOT_TOKEN and TELEGRAM_ALLOWED_CHAT_IDS")
    client = Frappe.from_env()
    offset = 0
    while True:
        try:
            for u in telegram.api("getUpdates", offset=offset, timeout=50):
                offset = u["update_id"] + 1
                if "callback_query" in u:
                    handle_callback(client, u["callback_query"])
                elif "message" in u:
                    handle_message(client, u["message"])
        except Exception as e:  # log the type only: request errors can embed the token URL
            print("bot error:", type(e).__name__, flush=True)
            time.sleep(5)


if __name__ == "__main__":
    main()

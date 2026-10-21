"""Minimal Telegram Bot API access over plain HTTPS. Only chats in TELEGRAM_ALLOWED_CHAT_IDS are served."""
import os

import requests

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ALLOWED = [int(x) for x in os.environ.get("TELEGRAM_ALLOWED_CHAT_IDS", "").replace(" ", "").split(",") if x]
ACTIONS = ("Business", "Spam", "Trash")


def api(method, **params):
    r = requests.post(f"https://api.telegram.org/bot{TOKEN}/{method}", json=params, timeout=70)
    if not r.ok:  # not raise_for_status: its message would put the token URL in logs
        raise RuntimeError(f"telegram {method}: {r.status_code} {r.text[:200]}")
    return r.json()["result"]


def keyboard(bill):
    return {"inline_keyboard": [[{"text": a, "callback_data": f"{a}:{bill}"} for a in ACTIONS]]}


def notify(text, bill=None):
    """Message every allowed chat; no-op when Telegram is not configured."""
    if not TOKEN:
        return
    for chat in ALLOWED:
        extra = {"reply_markup": keyboard(bill)} if bill else {}
        api("sendMessage", chat_id=chat, text=text, **extra)

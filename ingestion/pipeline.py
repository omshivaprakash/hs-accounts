"""Shared ingest step used by the folder watcher and the Telegram bot."""
import hashlib
import os
from pathlib import Path

from . import ocr, parser

INBOX = Path(os.environ.get("INBOX_DIR", "inbox"))
LOW_CONFIDENCE = 0.75


def ingest(client, path, source):
    """Create a Bill (with the original attached) from a file. Never deletes the file."""
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    if existing := client.find_by_hash(digest):
        return {"name": existing, "duplicate": True}

    text, confidence = ocr.extract_text(path)
    fields = parser.parse(text)
    missing = [k for k in parser.REQUIRED if k not in fields]
    needs_review = int(confidence < LOW_CONFIDENCE or bool(missing))
    doc = {
        **fields,
        "source": source,
        "file_hash": digest,
        "ocr_confidence": round(confidence * 100, 1),
        "ocr_text": text,
        "needs_review": needs_review,
    }
    name = client.create_bill(doc)
    try:
        client.attach(name, path)
    except Exception:
        client.delete_bill(name)  # a bill without its source file must not exist; the file stays on disk
        raise
    return {
        "name": name,
        "duplicate": False,
        "needs_review": needs_review,
        "missing": missing,
        "vendor": fields.get("vendor"),
        "grand_total": fields.get("grand_total"),
    }


def summary(res):
    if res["duplicate"]:
        return f"Already ingested as {res['name']}"
    line = f"{res['name']}: {res['vendor'] or '?'}, Rs {res['grand_total'] or '?'}"
    if res["needs_review"]:
        line += "\nNeeds review" + (f" (missing: {', '.join(res['missing'])})" if res["missing"] else " (low OCR confidence)")
    return line

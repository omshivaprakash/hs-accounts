"""Regex parser for Indian GST invoices. Missing fields are reported so a human reviews the bill.

shortcut: covers common layouts only, amounts need two decimals, no line items; upgrade to a layout/LLM extractor if review volume is high.
shortcut: vendor GSTIN is the first GSTIN in the text, which is the seller on nearly all invoices.
"""
import re
from datetime import date

MONEY = re.compile(r"\d[\d,]*\.\d{2}")
GSTIN = re.compile(r"\b\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]\b")
INVOICE_NO = re.compile(r"invoice\s*(?:no\.?|number|#)\s*[:#\-]?\s*([A-Z0-9][A-Z0-9/\-]{2,})", re.I)
SELLER = re.compile(r"(?:sold by|billed by|supplier)\s*[:\-]\s*([^,\n]+)", re.I)
NOISE = re.compile(r"^(tax\s+invoice|invoice|bill|original|duplicate|gstin|cash\s*memo|page)\b", re.I)
DMY = re.compile(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b")
D_MON_Y = re.compile(r"\b(\d{1,2})[ -]([A-Za-z]{3})[a-z]*[ ,-]+(\d{4})\b")
MONTHS = "jan feb mar apr may jun jul aug sep oct nov dec".split()
TOTAL_KEYS = [r"grand\s*total", r"total\s*amount", r"amount\s*payable", r"net\s*payable", r"invoice\s*total", r"^total\b"]
NOT_TOTAL = r"sub\s*total|total\s+tax|tax\s+amount|before\s+tax"

REQUIRED = ("vendor", "invoice_no", "bill_date", "grand_total")


def _num(s):
    return float(s.replace(",", ""))


def _date_in(line):
    m = DMY.search(line)
    if m:
        d, mo, y = map(int, m.groups())
    else:
        m = D_MON_Y.search(line)
        if not m or m.group(2).lower() not in MONTHS:
            return None
        d, y, mo = int(m.group(1)), int(m.group(3)), MONTHS.index(m.group(2).lower()) + 1
    try:
        return date(y, mo, d).isoformat()
    except ValueError:
        return None


def _bill_date(lines):
    for line in lines:
        if re.search(r"date", line, re.I) and not re.search(r"due", line, re.I) and (d := _date_in(line)):
            return d
    return next((d for line in lines if (d := _date_in(line))), None)


def _last_amount(lines, key, skip=None):
    """Last money value on the last line matching key (summary rows sit below item rows)."""
    found = None
    for line in lines:
        if re.search(key, line, re.I) and not (skip and re.search(skip, line, re.I)):
            money = MONEY.findall(line)
            if money:
                found = _num(money[-1])
    return found


def _grand_total(lines):
    for key in TOTAL_KEYS:
        if (v := _last_amount(lines, key, NOT_TOTAL)) is not None:
            return v


def _invoice_no(text):
    return next((m.group(1) for m in INVOICE_NO.finditer(text) if any(c.isdigit() for c in m.group(1))), None)


def _vendor(text, lines):
    if m := SELLER.search(text):
        return m.group(1).strip()
    return next((l for l in lines if re.search(r"[A-Za-z]{3}", l) and not NOISE.match(l)), None)


def parse(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    gstin = GSTIN.search(text)
    out = {
        "vendor": _vendor(text, lines),
        "vendor_gstin": gstin.group() if gstin else None,
        "invoice_no": _invoice_no(text),
        "bill_date": _bill_date(lines),
        "cgst": _last_amount(lines, r"\bCGST\b"),
        "sgst": _last_amount(lines, r"\bSGST\b"),
        "igst": _last_amount(lines, r"\bIGST\b"),
        "grand_total": _grand_total(lines),
    }
    if out["grand_total"] is not None:
        taxes = sum(out[k] or 0 for k in ("cgst", "sgst", "igst"))
        out["net_amount"] = round(out["grand_total"] - taxes, 2)
    return {k: v for k, v in out.items() if v is not None}

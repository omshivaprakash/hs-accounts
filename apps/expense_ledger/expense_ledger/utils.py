"""Pure helpers, kept free of frappe imports so they can be unit-tested anywhere."""
from datetime import date


def financial_year(d: date) -> str:
    """Indian FY (April to March), e.g. 2026-04-01 -> '2026-27'."""
    start = d.year if d.month >= 4 else d.year - 1
    return f"{start}-{str(start + 1)[-2:]}"


def match_rule(vendor: str, rules: list[dict]) -> dict | None:
    """Longest vendor_pattern contained in the vendor name wins (case-insensitive)."""
    v = (vendor or "").lower()
    hits = [r for r in rules if r["vendor_pattern"] and r["vendor_pattern"].lower() in v]
    return max(hits, key=lambda r: len(r["vendor_pattern"])) if hits else None


def totals(net, cgst, sgst, igst, grand, tolerance=1.0):
    """Fill whichever of net/grand is missing and report whether net + tax == grand."""
    net, cgst, sgst, igst, grand = (float(x or 0) for x in (net, cgst, sgst, igst, grand))
    tax = round(cgst + sgst + igst, 2)
    if grand and not net:
        net = round(grand - tax, 2)
    elif net and not grand:
        grand = round(net + tax, 2)
    consistent = bool(grand) and abs(net + tax - grand) <= tolerance
    return net, tax, grand, consistent

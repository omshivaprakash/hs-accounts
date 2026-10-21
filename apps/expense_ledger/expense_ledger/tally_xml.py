"""Builds Tally import files: ledger masters, and purchase vouchers for confirmed bills. Pure, no frappe.

shortcut: the accountant's exact template is still open, so this is Tally's standard XML import. Vendors
become Sundry Creditors and categories become expense (or, for capex, fixed asset) ledgers; import the
masters file first, then the vouchers. Revisit once the accountant confirms the layout they want.
"""
from xml.sax.saxutils import escape, quoteattr

HEAD = '<?xml version="1.0" encoding="UTF-8"?>'


def _envelope(report, company, messages):
    return (
        f"{HEAD}<ENVELOPE><HEADER><TALLYREQUEST>Import Data</TALLYREQUEST></HEADER><BODY><IMPORTDATA>"
        f"<REQUESTDESC><REPORTNAME>{report}</REPORTNAME><STATICVARIABLES>"
        f"<SVCURRENTCOMPANY>{escape(company)}</SVCURRENTCOMPANY></STATICVARIABLES></REQUESTDESC>"
        f'<REQUESTDATA>{"".join(messages)}</REQUESTDATA></IMPORTDATA></BODY></ENVELOPE>'
    )


def _message(body):
    return f'<TALLYMESSAGE xmlns:UDF="TallyUDF">{body}</TALLYMESSAGE>'


def _entry(ledger, amount, debit):
    # Tally writes debits as negative amounts on "deemed positive" lines
    return (
        f"<ALLLEDGERENTRIES.LIST><LEDGERNAME>{escape(ledger)}</LEDGERNAME>"
        f"<ISDEEMEDPOSITIVE>{'Yes' if debit else 'No'}</ISDEEMEDPOSITIVE>"
        f"<AMOUNT>{-amount if debit else amount:.2f}</AMOUNT></ALLLEDGERENTRIES.LIST>"
    )


def _ledger_of(bill, categories):
    return categories.get(bill["expense_category"], (bill["expense_category"], 0))[0]


def _voucher(bill, categories, gst):
    taxes = {k: float(bill.get(k) or 0) for k in ("cgst", "sgst", "igst")}
    total = float(bill["grand_total"] or 0)
    base = round(total - sum(taxes.values()), 2)  # derived so every voucher balances to the paisa
    entries = [_entry(bill["vendor"], total, False), _entry(_ledger_of(bill, categories), base, True)]
    entries += [_entry(gst[k], v, True) for k, v in taxes.items() if v]
    narration = f"{bill['vendor']} inv {bill['invoice_no']} (paid by {bill.get('paid_by') or '-'}, {bill.get('payment_mode') or '-'})"
    return _message(
        '<VOUCHER VCHTYPE="Purchase" ACTION="Create" OBJVIEW="Accounting Voucher View">'
        f"<DATE>{str(bill['bill_date']).replace('-', '')}</DATE><VOUCHERTYPENAME>Purchase</VOUCHERTYPENAME>"
        f"<VOUCHERNUMBER>{escape(bill['name'])}</VOUCHERNUMBER><REFERENCE>{escape(bill['invoice_no'])}</REFERENCE>"
        f"<PARTYLEDGERNAME>{escape(bill['vendor'])}</PARTYLEDGERNAME><NARRATION>{escape(narration)}</NARRATION>"
        f'{"".join(entries)}</VOUCHER>'
    )


def vouchers_xml(bills, categories, company, gst):
    """categories: {name: (tally ledger, is_capex)}; gst: {"cgst"|"sgst"|"igst": ledger name}."""
    return _envelope("Vouchers", company, [_voucher(b, categories, gst) for b in bills])


def masters_xml(bills, categories, company, gst):
    wanted = {}  # ledger name -> parent group; first writer wins
    for b in bills:
        wanted.setdefault(b["vendor"], "Sundry Creditors")
        name, capex = categories.get(b["expense_category"], (b["expense_category"], 0))
        wanted.setdefault(name, "Fixed Assets" if capex else "Indirect Expenses")
        for k in ("cgst", "sgst", "igst"):
            if b.get(k):
                wanted.setdefault(gst[k], "Duties & Taxes")
    msgs = [
        _message(f'<LEDGER NAME={quoteattr(n)} ACTION="Create"><NAME>{escape(n)}</NAME><PARENT>{escape(p)}</PARENT></LEDGER>')
        for n, p in wanted.items()
    ]
    return _envelope("All Masters", company, msgs)

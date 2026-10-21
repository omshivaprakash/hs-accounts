import xml.etree.ElementTree as ET

from expense_ledger import tally_xml, utils

BILLS = [
    {"name": "BILL-2026-00001", "vendor": "R&D Traders", "invoice_no": "T/1", "bill_date": "2026-10-14", "expense_category": "R&D Materials",
     "cgst": 90, "sgst": 90, "igst": 0, "grand_total": 1180, "paid_by": "Kiran", "payment_mode": "Personal UPI"},
    {"name": "BILL-2026-00002", "vendor": "Fibre Co", "invoice_no": "F9", "bill_date": "2026-10-15", "expense_category": "Capex Item",
     "cgst": 0, "sgst": 0, "igst": 180, "grand_total": 1180.5, "paid_by": "Company", "payment_mode": "Bank Transfer"},
]
CATS = {"R&D Materials": ("Research Materials", 0), "Capex Item": ("Capital Equipment", 1)}
GST = {"cgst": "Input CGST", "sgst": "Input SGST", "igst": "Input IGST"}


def amounts(voucher):
    return [float(a.text) for a in voucher.iter("AMOUNT")]


def test_every_voucher_balances_and_special_characters_survive():
    root = ET.fromstring(tally_xml.vouchers_xml(BILLS, CATS, "Acme & Co", GST))
    assert root.find(".//SVCURRENTCOMPANY").text == "Acme & Co"
    vouchers = list(root.iter("VOUCHER"))
    assert len(vouchers) == 2
    for v in vouchers:
        assert abs(sum(amounts(v))) < 0.005
    first = vouchers[0]
    assert first.find("PARTYLEDGERNAME").text == "R&D Traders"
    assert first.find("DATE").text == "20261014"
    assert [e.find("LEDGERNAME").text for e in first.iter("ALLLEDGERENTRIES.LIST")] == ["R&D Traders", "Research Materials", "Input CGST", "Input SGST"]
    assert amounts(vouchers[1]) == [1180.5, -1000.5, -180.0]  # purchase ledger is derived from the total


def test_masters_cover_vendors_categories_and_used_taxes_only():
    root = ET.fromstring(tally_xml.masters_xml(BILLS, CATS, "Acme", GST))
    got = {l.get("NAME"): l.find("PARENT").text for l in root.iter("LEDGER")}
    assert got == {
        "R&D Traders": "Sundry Creditors",
        "Research Materials": "Indirect Expenses",
        "Input CGST": "Duties & Taxes",
        "Input SGST": "Duties & Taxes",
        "Fibre Co": "Sundry Creditors",
        "Capital Equipment": "Fixed Assets",
        "Input IGST": "Duties & Taxes",
    }


def test_claim_groups_split_by_payee_and_optionally_category():
    bills = [
        {"name": "1", "paid_by": "Kiran", "expense_category": "Travel"},
        {"name": "2", "paid_by": "Kiran", "expense_category": "Fuel"},
        {"name": "3", "paid_by": "Om", "expense_category": "Travel"},
    ]
    assert {k: len(v) for k, v in utils.claim_groups(bills).items()} == {("Kiran", None): 2, ("Om", None): 1}
    assert len(utils.claim_groups(bills, by_category=True)) == 3

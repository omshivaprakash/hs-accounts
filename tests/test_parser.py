from ingestion import parser

INTRA_STATE = """SHARMA ELECTRONICS
GSTIN: 29ABCDE1234F1Z5
Tax Invoice
Invoice No: SE/2026/0417
Invoice Date: 14/10/2026
Due Date: 30/10/2026
Item  Qty  Rate  Amount
Cable  2  500.00  1000.00
CGST @9%  90.00
SGST @9%  90.00
Grand Total  1180.00
"""


def test_intra_state_invoice():
    r = parser.parse(INTRA_STATE)
    assert r["vendor"] == "SHARMA ELECTRONICS"
    assert r["vendor_gstin"] == "29ABCDE1234F1Z5"
    assert r["invoice_no"] == "SE/2026/0417"
    assert r["bill_date"] == "2026-10-14"  # not the due date
    assert (r["cgst"], r["sgst"]) == (90.0, 90.0)
    assert r["grand_total"] == 1180.0
    assert r["net_amount"] == 1000.0
    assert "igst" not in r


def test_inter_state_with_seller_label_and_month_name():
    r = parser.parse(
        "Sold By: Cloudtail India, Bengaluru\nInvoice Number : BLR7-12345\n"
        "Date: 03-Oct-2026\nIGST @18%  180.00\nTotal Amount  1,180.00\nSub Total 1000.00"
    )
    assert r["vendor"] == "Cloudtail India"
    assert r["invoice_no"] == "BLR7-12345"
    assert r["bill_date"] == "2026-10-03"
    assert r["igst"] == 180.0
    assert r["grand_total"] == 1180.0


def test_garbage_reports_missing_fields():
    r = parser.parse("xx\n!!\n")
    assert [k for k in parser.REQUIRED if k not in r] == ["vendor", "invoice_no", "bill_date", "grand_total"]

from datetime import date

from expense_ledger import utils


def test_financial_year_boundaries():
    assert utils.financial_year(date(2026, 3, 31)) == "2025-26"
    assert utils.financial_year(date(2026, 4, 1)) == "2026-27"
    assert utils.financial_year(date(2099, 12, 31)) == "2099-00"


def test_match_rule_prefers_longest_pattern():
    rules = [
        {"vendor_pattern": "amazon", "expense_category": "R&D Materials"},
        {"vendor_pattern": "amazon web services", "expense_category": "Software/SaaS"},
    ]
    assert utils.match_rule("Amazon Web Services India", rules)["expense_category"] == "Software/SaaS"
    assert utils.match_rule("AMAZON SELLER", rules)["expense_category"] == "R&D Materials"
    assert utils.match_rule("Rohu Traders", rules) is None


def test_totals_fill_and_consistency():
    assert utils.totals(None, 90, 90, 0, 1180) == (1000.0, 180.0, 1180.0, True)
    assert utils.totals(1000, 90, 90, 0, None) == (1000.0, 180.0, 1180.0, True)
    assert utils.totals(1000, 90, 90, 0, 1500)[3] is False
    assert utils.totals(None, None, None, None, None)[3] is False

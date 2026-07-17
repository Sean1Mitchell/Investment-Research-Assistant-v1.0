"""
Accounting-identity validation, generalized from the per-parser checks
built during this project (income statement's gross-profit check,
balance sheet's assets=liabilities+equity, cash flow's derived total).
Centralizing these here means any parser's output can be validated the
same way, rather than each parser reimplementing its own check.
"""

def check_balance_sheet(mapped, tolerance=1):
    """Total assets = Total liabilities + Equity."""
    assets = mapped.get("total_assets")
    liabilities = mapped.get("total_liabilities")
    equity = mapped.get("equity")
    if not (assets and liabilities and equity):
        return {"checked": False, "consistent": False, "reason": "missing required figures"}

    results = [abs((a + l) - e) <= tolerance for a, l, e in zip(assets, liabilities, equity)]
    return {"checked": True, "consistent": all(results)}


def check_income_statement(mapped, tolerance=1):
    """Revenue - Cost of sales (and similar deductions) should reconcile to Gross profit."""
    revenue = mapped.get("revenue")
    cost_of_sales = mapped.get("cost_of_sales")
    gross_profit = mapped.get("gross_profit")
    if not (revenue and cost_of_sales and gross_profit):
        return {"checked": False, "consistent": False, "reason": "missing required figures"}

    results = [abs((r + c) - g) <= tolerance for r, c, g in zip(revenue, cost_of_sales, gross_profit)]
    return {"checked": True, "consistent": all(results)}


def check_cash_flow(mapped, tolerance_fn=lambda start: max(5, abs(start) * 0.02)):
    """Operating + Investing + Financing should reconcile to the change in cash balance."""
    operating = mapped.get("net_cash_operating")
    investing = mapped.get("net_cash_investing")
    financing = mapped.get("net_cash_financing")
    start = mapped.get("cash_at_beginning")
    end = mapped.get("cash_at_end")

    if not all([operating, investing, financing, start]):
        return {"checked": False, "consistent": False, "reason": "missing required figures"}
    if not end:
        return {"checked": False, "consistent": False, "reason": "cash_at_end could not be parsed"}

    results = []
    for o, i, f, s, e in zip(operating, investing, financing, start, end):
        derived = o + i + f
        actual = e - s
        results.append(abs(derived - actual) <= tolerance_fn(s))

    return {"checked": True, "consistent": all(results)}


VALIDATORS = {
    "balance_sheet": check_balance_sheet,
    "income_statement": check_income_statement,
    "cash_flow": check_cash_flow,
}

"""
Defines the canonical set of accounting concepts this system understands,
independent of any single company's wording or any single PDF's layout.
Each concept has a standard name, the statement it belongs to, and its
IFRS category — this is the vocabulary everything else maps onto.
"""

BALANCE_SHEET = "balance_sheet"
INCOME_STATEMENT = "income_statement"
CASH_FLOW = "cash_flow"

CONCEPTS = {
    # --- Balance Sheet ---
    "inventory": {"statement": BALANCE_SHEET, "category": "current_asset"},
    "cash_and_cash_equivalents": {"statement": BALANCE_SHEET, "category": "current_asset"},
    "trade_receivables": {"statement": BALANCE_SHEET, "category": "current_asset"},
    "property_plant_equipment": {"statement": BALANCE_SHEET, "category": "non_current_asset"},
    "intangible_assets": {"statement": BALANCE_SHEET, "category": "non_current_asset"},
    "non_current_assets_total": {"statement": BALANCE_SHEET, "category": "non_current_asset_total"},
    "current_assets_total": {"statement": BALANCE_SHEET, "category": "current_asset_total"},
    "trade_payables": {"statement": BALANCE_SHEET, "category": "current_liability"},
    "borrowings": {"statement": BALANCE_SHEET, "category": "liability"},
    "non_current_liabilities_total": {"statement": BALANCE_SHEET, "category": "non_current_liability_total"},
    "current_liabilities_total": {"statement": BALANCE_SHEET, "category": "current_liability_total"},
    "total_assets": {"statement": BALANCE_SHEET, "category": "total"},
    "total_liabilities": {"statement": BALANCE_SHEET, "category": "total"},
    "equity": {"statement": BALANCE_SHEET, "category": "equity"},

    # --- Income Statement ---
    "revenue": {"statement": INCOME_STATEMENT, "category": "income"},
    "cost_of_sales": {"statement": INCOME_STATEMENT, "category": "expense"},
    "gross_profit": {"statement": INCOME_STATEMENT, "category": "subtotal"},
    "operating_profit": {"statement": INCOME_STATEMENT, "category": "subtotal"},
    "finance_costs": {"statement": INCOME_STATEMENT, "category": "expense"},
    "profit_before_tax": {"statement": INCOME_STATEMENT, "category": "subtotal"},
    "tax_expense": {"statement": INCOME_STATEMENT, "category": "expense"},
    "profit_after_tax": {"statement": INCOME_STATEMENT, "category": "total"},

    # --- Cash Flow ---
    "net_cash_operating": {"statement": CASH_FLOW, "category": "activity_total"},
    "net_cash_investing": {"statement": CASH_FLOW, "category": "activity_total"},
    "net_cash_financing": {"statement": CASH_FLOW, "category": "activity_total"},
    "cash_at_beginning": {"statement": CASH_FLOW, "category": "balance"},
    "cash_at_end": {"statement": CASH_FLOW, "category": "balance"},
}

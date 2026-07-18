"""
Maps each accounting concept to every real-world label variant we've
encountered across companies. This is the file that grows over time as
new companies introduce new wording — the ONE place that needs updating,
rather than touching parser logic per company.
"""

ALIASES = {
    "inventory": ["inventory", "inventories", "stock"],
    "cash_and_cash_equivalents": ["cash and cash equivalents"],
    "trade_receivables": ["trade and other receivables", "trade receivables"],
    "property_plant_equipment": ["property, plant and equipment"],
    "intangible_assets": ["goodwill and other intangible assets", "intangible assets"],
    "non_current_assets_total": ["non-current assets"],
    "current_assets_total": ["current assets"],
    "trade_payables": ["trade and other payables", "trade payables"],
    "borrowings": ["borrowings"],
    "non_current_liabilities_total": ["non-current liabilities"],
    "current_liabilities_total": ["current liabilities"],
    "total_assets": ["total assets"],
    "total_liabilities": ["total liabilities"],
    "equity": ["total equity", "net assets"],

    "revenue": ["revenue"],
    "cost_of_sales": ["cost of sales"],
    "gross_profit": ["gross profit"],
    "operating_profit": ["operating profit"],
    "finance_costs": ["finance costs", "finance expense"],
    "profit_before_tax": [
        "profit/(loss) before tax from continuing operations",
        "profit/(loss) before tax - continuing operations",
    ],
    "tax_expense": ["income tax", "taxation"],
    "profit_after_tax": [
        "profit/(loss) for the year",
        "profit/(loss) for the financial period",
    ],

    "net_cash_operating": [
        "net cash generated from operating",
        "net cash used in operating",
        "net cash generated from/(used in) operating",
    ],
    "net_cash_investing": [
        "net cash used in investing",
        "net cash generated from investing",
        "net cash generated from/(used in) investing",
    ],
    "net_cash_financing": [
        "net cash used in financing",
        "net cash generated from financing",
        "net cash generated from/(used in) financing",
    ],
    "cash_at_beginning": ["opening cash and cash equivalents", "cash and cash equivalents at the beginning"],
    "cash_at_end": ["closing cash and cash equivalents", "cash and cash equivalents at the end"],
}

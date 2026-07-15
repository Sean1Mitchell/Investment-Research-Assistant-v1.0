import pdfplumber
import re

# Each entry: (required_all, required_any)
# required_all: every keyword must be present in the line
# required_any: at least one of these must be present (skipped if empty list)
LINE_ITEM_RULES = {
    "revenue": (["revenue"], []),
    "cost_of_sales": (["cost of sales"], []),
    "gross_profit": (["gross profit"], []),
    "operating_profit": (["operating profit"], []),
    "profit_before_tax": (["profit", "before tax"], []),
    "taxation": ([], ["income tax", "taxation"]),
    "profit_for_year": (["profit"], ["for the year", "for the financial period"]),
}

def line_matches(line, required_all, required_any):
    lower = line.lower()
    if required_all and not all(k in lower for k in required_all):
        return False
    if required_any and not any(k in lower for k in required_any):
        return False
    return True

def extract_numbers(line):
    pattern = r"\(?-?[\d,]+\)?|[-\u2013\u2014]"
    raw = re.findall(pattern, line)
    numbers = []
    for r in raw:
        r = r.strip()
        if r in ("-", "\u2013", "\u2014"):
            numbers.append(0)
        else:
            negative = r.startswith("(")
            cleaned = r.replace("(", "").replace(")", "").replace(",", "")
            if cleaned.isdigit():
                value = int(cleaned)
                numbers.append(-value if negative else value)
    return numbers

def parse_income_statement(filepath, page_index):
    """
    Extracts key income statement line items from a given page of a PDF.
    Returns a dict of {line_item: {"this_year_total": int, "last_year_total": int}}.

    Note: page_index must currently be found manually via the company's
    table of contents (printed page number + 1). Automatic page discovery
    is a planned improvement, not yet built.
    """
    with pdfplumber.open(filepath) as pdf:
        page = pdf.pages[page_index]
        text = page.extract_text()

    lines = text.split("\n")
    results = {}

    for key, (required_all, required_any) in LINE_ITEM_RULES.items():
        for line in lines:
            if line_matches(line, required_all, required_any):
                numbers = extract_numbers(line)
                if len(numbers) >= 6:
                    last_six = numbers[-6:]
                    results[key] = {
                        "this_year_total": last_six[2],
                        "last_year_total": last_six[5]
                    }
    return results

import pdfplumber
import re

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

def extract_line_total(line):
    numbers = extract_numbers(line)
    if len(numbers) >= 6:
        return numbers[-6:][2]
    elif len(numbers) >= 1:
        return numbers[-1]
    return None

def extract_period_end_dates(lines):
    date_pattern = re.compile(r"(\d{1,2} \w+ \d{4})")
    for line in lines[:6]:
        dates = date_pattern.findall(line)
        if len(dates) == 2:
            return dates[0], dates[1]
    return None, None

def find_income_statement_page(filepath):
    with pdfplumber.open(filepath) as pdf:
        for i in range(len(pdf.pages)):
            page = pdf.pages[i]
            text = page.extract_text()
            page.flush_cache()
            if not text:
                continue
            lower = text.lower()
            if ("income statement" in lower
                    and "revenue" in lower
                    and "cost of sales" in lower
                    and "operating profit" in lower):
                return i
    return None

def check_gross_profit_consistency(lines):
    start_index = None
    end_index = None
    for i, line in enumerate(lines):
        lower = line.lower()
        if start_index is None and lower.startswith("revenue") and "from sale" not in lower:
            start_index = i
        if "gross profit" in lower:
            end_index = i
            break
    if start_index is None or end_index is None:
        return {"checked": False, "consistent": False}

    running_total = 0
    for line in lines[start_index:end_index]:
        value = extract_line_total(line)
        if value is not None:
            running_total += value

    stated_gross_profit = extract_line_total(lines[end_index])
    difference = abs(running_total - stated_gross_profit) if stated_gross_profit is not None else None

    return {
        "checked": True,
        "consistent": difference is not None and difference <= 1
    }

def parse_income_statement(filepath, page_index=None):
    """
    Extracts key income statement line items from a PDF, tagged with their
    real fiscal year-end dates, plus a consistency check result.

    Returns:
        {
            "statement_type": "income_statement",
            "consistency_check": {...},
            "years": {
                "<this_year_end_date>": {"revenue": 123, ...},
                "<last_year_end_date>": {"revenue": 456, ...},
            }
        }
    """
    if page_index is None:
        page_index = find_income_statement_page(filepath)
        if page_index is None:
            raise ValueError(f"Could not locate income statement page in {filepath}")

    with pdfplumber.open(filepath) as pdf:
        page = pdf.pages[page_index]
        text = page.extract_text()

    lines = text.split("\n")
    this_year_end, last_year_end = extract_period_end_dates(lines)

    this_year_figures = {}
    last_year_figures = {}

    for key, (required_all, required_any) in LINE_ITEM_RULES.items():
        for line in lines:
            if line_matches(line, required_all, required_any):
                numbers = extract_numbers(line)
                if len(numbers) >= 6:
                    last_six = numbers[-6:]
                    this_year_figures[key] = last_six[2]
                    last_year_figures[key] = last_six[5]

    consistency = check_gross_profit_consistency(lines)

    return {
        "statement_type": "income_statement",
        "consistency_check": consistency,
        "years": {
            this_year_end: this_year_figures,
            last_year_end: last_year_figures,
        }
    }

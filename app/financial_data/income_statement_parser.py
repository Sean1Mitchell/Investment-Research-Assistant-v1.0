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
    """
    Sums every line between 'Revenue' and 'Gross profit' (inclusive of
    revenue), and checks it against the stated gross profit total. This
    generalizes across companies with different numbers of deduction lines
    (e.g. Tesco's insurance-related lines vs Sainsbury's simpler structure),
    rather than assuming a fixed revenue-minus-cost-of-sales formula.
    """
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
    Extracts key income statement line items from a PDF, and runs a
    consistency check to flag whether the extraction looks internally sound.
    Returns a dict of {line_item: {"this_year_total": int, "last_year_total": int}}
    plus a "_consistency_check" entry with the check result.
    """
    if page_index is None:
        page_index = find_income_statement_page(filepath)
        if page_index is None:
            raise ValueError(f"Could not locate income statement page in {filepath}")

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

    results["_consistency_check"] = check_gross_profit_consistency(lines)
    return results

import pdfplumber
import re
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "ifrs"))
from taxonomy import match_label_to_concept

def group_words_into_lines(words, y_tolerance=3):
    lines = {}
    for w in words:
        y_key = round(w["top"] / y_tolerance) * y_tolerance
        lines.setdefault(y_key, []).append(w)
    return lines

def line_text(word_list):
    return " ".join(w["text"] for w in sorted(word_list, key=lambda w: w["x0"]))

def has_letters(text):
    return any(c.isalpha() for c in text)

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

def merge_split_lines(lines_dict, year_count):
    sorted_keys = sorted(lines_dict.keys())
    merged = {}
    skip_next = False
    for i, y in enumerate(sorted_keys):
        if skip_next:
            skip_next = False
            continue
        text = line_text(lines_dict[y])
        if i + 1 < len(sorted_keys):
            next_y = sorted_keys[i + 1]
            next_text = line_text(lines_dict[next_y])
            this_line_numbers = extract_numbers(text)
            if (has_letters(text) and not has_letters(next_text)
                    and 0 < len(this_line_numbers) < year_count):
                text = text + " " + next_text
                skip_next = True
        merged[y] = text
    return merged

def find_column_boundary(words, page_width):
    x_positions = sorted(set(round(w["x0"]) for w in words))
    gaps = []
    for i in range(1, len(x_positions)):
        gap_size = x_positions[i] - x_positions[i-1]
        midpoint = (x_positions[i-1] + x_positions[i]) / 2
        gaps.append((gap_size, midpoint, x_positions[i-1], x_positions[i]))
    center = page_width / 2
    center_tolerance = page_width * 0.15
    near_center_gaps = [g for g in gaps if abs(g[1] - center) <= center_tolerance]
    if not near_center_gaps:
        near_center_gaps = gaps
    near_center_gaps.sort(reverse=True)
    best = near_center_gaps[0]
    return (best[2] + best[3]) / 2

def detect_year_count(lines):
    year_pattern = re.compile(r"\b20\d{2}\b")
    combined_text = " ".join(lines[:8])
    years_found = set(year_pattern.findall(combined_text))
    return len(years_found) if len(years_found) >= 2 else 2

def reconstruct_reading_order(words, page_width, year_count):
    boundary = find_column_boundary(words, page_width)
    left_words = [w for w in words if w["x0"] < boundary]
    right_words = [w for w in words if w["x0"] >= boundary]
    left_lines_raw = group_words_into_lines(left_words)
    right_lines_raw = group_words_into_lines(right_words)
    left_lines = merge_split_lines(left_lines_raw, year_count)
    right_lines = merge_split_lines(right_lines_raw, year_count)
    ordered = []
    for y in sorted(left_lines.keys()):
        ordered.append(left_lines[y])
    for y in sorted(right_lines.keys()):
        ordered.append(right_lines[y])
    return ordered

def extract_period_end_dates(lines, year_count):
    combined_text = " ".join(lines[:8])
    full_date_pattern = re.compile(r"\d{1,2} \w+ 20\d{2}")
    full_dates = full_date_pattern.findall(combined_text)
    if len(full_dates) >= year_count:
        return full_dates[:year_count]

    day_month_pattern = re.compile(
        r"\b\d{1,2} (?:January|February|March|April|May|June|July|August|September|October|November|December)\b"
    )
    year_pattern = re.compile(r"\b20\d{2}\b")
    day_months = day_month_pattern.findall(combined_text)
    years = sorted(set(year_pattern.findall(combined_text)), reverse=True)
    day_months = day_months[:year_count]
    years = years[:year_count]
    if len(day_months) == year_count and len(years) == year_count:
        return [f"{day_months[i]} {years[i]}" for i in range(year_count)]
    return [None] * year_count

def find_cash_flow_page(filepath):
    with pdfplumber.open(filepath) as pdf:
        for i in range(len(pdf.pages)):
            page = pdf.pages[i]
            text = page.extract_text()
            page.flush_cache()
            if not text:
                continue
            lower = text.lower()
            if ("cash flow statement" in lower
                    and "operating activities" in lower
                    and "investing activities" in lower
                    and "financing activities" in lower):
                return i
    return None

def check_cash_flow_consistency(derived_net_increase, cash_at_beginning, cash_at_end):
    if not derived_net_increase or not cash_at_beginning:
        return {"checked": False, "consistent": False, "reason": "missing required figures"}
    if not cash_at_end:
        return {"checked": False, "consistent": False, "reason": "cash_at_end could not be parsed for this report"}

    results = []
    for net, start, end in zip(derived_net_increase, cash_at_beginning, cash_at_end):
        actual_change = end - start
        difference = abs(actual_change - net)
        tolerance = max(5, abs(start) * 0.02)
        results.append(difference <= tolerance)

    return {"checked": True, "consistent": all(results)}

def parse_cash_flow_statement(filepath, page_index=None):
    """
    Extracts key cash flow figures using the IFRS taxonomy for label
    matching, replacing the previous hardcoded LINE_ITEM_KEYWORDS
    dictionary. All column-splitting, line-merging, and derivation logic
    (net_increase_in_cash_derived) is preserved unchanged — these are
    layout/arithmetic concerns, not label-wording concerns.
    """
    if page_index is None:
        page_index = find_cash_flow_page(filepath)
        if page_index is None:
            raise ValueError(f"Could not locate cash flow statement page in {filepath}")

    with pdfplumber.open(filepath) as pdf:
        page = pdf.pages[page_index]
        words = page.extract_words()
        page_width = page.width

    boundary_check_lines = reconstruct_reading_order(words, page_width, year_count=2)
    year_count = detect_year_count(boundary_check_lines)
    reading_order_lines = reconstruct_reading_order(words, page_width, year_count)
    period_dates = extract_period_end_dates(reading_order_lines, year_count)

    results = {}
    for line in reading_order_lines:
        concept = match_label_to_concept(line, statement="cash_flow")
        if not concept:
            continue
        numbers = extract_numbers(line)
        if len(numbers) >= year_count:
            results[concept] = numbers[-year_count:]
            # No break — consistent with the income statement's "last
            # match wins" behaviour, in case any company's wording
            # produces an earlier false-positive sub-line match.

    net_increase_derived = None
    if all(k in results for k in ["net_cash_operating", "net_cash_investing", "net_cash_financing"]):
        net_increase_derived = [
            o + i + f for o, i, f in zip(
                results["net_cash_operating"],
                results["net_cash_investing"],
                results["net_cash_financing"]
            )
        ]
        results["net_increase_in_cash_derived"] = net_increase_derived

    consistency = check_cash_flow_consistency(
        net_increase_derived,
        results.get("cash_at_beginning"),
        results.get("cash_at_end"),
    )

    years_output = {}
    for i, date in enumerate(period_dates):
        if date is None:
            continue
        years_output[date] = {
            key: (values[i] if values else None)
            for key, values in results.items()
        }

    return {
        "statement_type": "cash_flow",
        "consistency_check": consistency,
        "years": years_output,
    }

import pdfplumber
import re

SECTION_HEADERS = [
    "non-current assets",
    "current assets",
    "non-current liabilities",
    "current liabilities",
    "equity",
]

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

def detect_year_count(lines_dict):
    year_pattern = re.compile(r"\b(20\d{2})\b")
    combined_text = ""
    for y in sorted(lines_dict.keys())[:6]:
        combined_text += " " + line_text(lines_dict[y])
    years_found = year_pattern.findall(combined_text)
    unique_years = set(years_found)
    return len(unique_years) if len(unique_years) >= 2 else 2

def extract_period_end_dates(lines_dict, year_count):
    """
    Extracts the stated 'as at' dates. Tries a clean single-line full-date
    match first (e.g. '28 February 2026'). If dates are split across lines
    (day-month on one line, year on another), falls back to: collecting
    all day-month fragments in reading order, and all distinct years,
    then sorting years DESCENDING and pairing positionally — since UK
    financial statements always present years most-recent-first, left to
    right, regardless of how the text happens to be split across lines.
    """
    combined_lines = [line_text(lines_dict[y]) for y in sorted(lines_dict.keys())[:6]]
    combined_text = " ".join(combined_lines)

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

def segment_column_into_sections(merged_lines):
    sections = {}
    current_section = None
    for y in sorted(merged_lines.keys()):
        text = merged_lines[y]
        lower = text.lower().strip()
        if lower in SECTION_HEADERS:
            current_section = lower
            sections[current_section] = []
            continue
        if current_section:
            sections[current_section].append(text)
    return sections

def section_subtotal(section_lines, year_count):
    last_bare = None
    last_total_labeled = None
    for line in section_lines:
        if not has_letters(line):
            numbers = extract_numbers(line)
            if len(numbers) >= year_count:
                last_bare = numbers[-year_count:]
        elif "total" in line.lower():
            numbers = extract_numbers(line)
            if len(numbers) >= year_count:
                last_total_labeled = numbers[-year_count:]
    return last_bare if last_bare else last_total_labeled

def find_balance_sheet_page(filepath):
    with pdfplumber.open(filepath) as pdf:
        for i in range(len(pdf.pages)):
            page = pdf.pages[i]
            text = page.extract_text()
            page.flush_cache()
            if not text:
                continue
            lower = text.lower()
            if ("balance sheet" in lower
                    and "non-current assets" in lower
                    and "current liabilities" in lower
                    and "equity" in lower):
                return i
    return None

def check_balance_sheet_consistency(total_assets, total_liabilities, equity):
    if not total_assets or not total_liabilities or not equity:
        return {"checked": False, "consistent": False}
    results = []
    for a, l, e in zip(total_assets, total_liabilities, equity):
        difference = abs((a + l) - e)
        results.append(difference <= 1)
    return {"checked": True, "consistent": all(results)}

def parse_balance_sheet(filepath, page_index=None):
    if page_index is None:
        page_index = find_balance_sheet_page(filepath)
        if page_index is None:
            raise ValueError(f"Could not locate balance sheet page in {filepath}")

    with pdfplumber.open(filepath) as pdf:
        page = pdf.pages[page_index]
        words = page.extract_words()
        page_width = page.width

    boundary = find_column_boundary(words, page_width)
    left_words = [w for w in words if w["x0"] < boundary]
    right_words = [w for w in words if w["x0"] >= boundary]

    left_lines_raw = group_words_into_lines(left_words)
    right_lines_raw = group_words_into_lines(right_words)

    year_count = detect_year_count(left_lines_raw)
    period_dates = extract_period_end_dates(left_lines_raw, year_count)

    left_lines = merge_split_lines(left_lines_raw, year_count)
    right_lines = merge_split_lines(right_lines_raw, year_count)

    left_sections = segment_column_into_sections(left_lines)
    right_sections = segment_column_into_sections(right_lines)
    all_sections = {**left_sections, **right_sections}

    section_values = {}
    for name, lines in all_sections.items():
        section_values[name] = section_subtotal(lines, year_count)

    non_curr_assets = section_values.get("non-current assets")
    curr_assets = section_values.get("current assets")
    non_curr_liab = section_values.get("non-current liabilities")
    curr_liab = section_values.get("current liabilities")
    equity = section_values.get("equity")

    total_assets = (
        [a + b for a, b in zip(non_curr_assets, curr_assets)]
        if non_curr_assets and curr_assets else None
    )
    total_liabilities = (
        [a + b for a, b in zip(non_curr_liab, curr_liab)]
        if non_curr_liab and curr_liab else None
    )

    consistency = check_balance_sheet_consistency(total_assets, total_liabilities, equity)

    years_output = {}
    for i, date in enumerate(period_dates):
        if date is None:
            continue
        years_output[date] = {
            "non_current_assets": non_curr_assets[i] if non_curr_assets else None,
            "current_assets": curr_assets[i] if curr_assets else None,
            "non_current_liabilities": non_curr_liab[i] if non_curr_liab else None,
            "current_liabilities": curr_liab[i] if curr_liab else None,
            "total_assets": total_assets[i] if total_assets else None,
            "total_liabilities": total_liabilities[i] if total_liabilities else None,
            "equity": equity[i] if equity else None,
        }

    return {
        "statement_type": "balance_sheet",
        "consistency_check": consistency,
        "years": years_output,
    }

"""
Takes raw extracted statement rows (label text + numeric values, already
correctly reconstructed by the layout/PDF layer) and maps each row to its
accounting concept using the IFRS taxonomy, producing a clean,
statement-agnostic dictionary.
"""

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "ifrs"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "financial_data"))
from taxonomy import match_label_to_concept
from income_statement_parser import extract_numbers  # reuse existing, proven number-parsing logic


def map_rows_to_concepts(rows, statement, year_count):
    """
    rows: list of raw text lines (already column-split/merged by the
          existing layout extraction — this function does NOT touch
          PDF coordinates at all, only text + numbers).
    statement: one of "balance_sheet", "income_statement", "cash_flow"
    year_count: how many year-columns of numbers to expect per row

    Returns: {concept_name: [value_year_1, value_year_2, ...]}
    """
    mapped = {}
    for row_text in rows:
        concept = match_label_to_concept(row_text, statement=statement)
        if not concept:
            continue
        numbers = extract_numbers(row_text)
        if len(numbers) >= year_count:
            mapped[concept] = numbers[-year_count:]

    return mapped

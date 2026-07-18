"""
Combines concepts.py and aliases.py into a single lookup: given a raw
label extracted from a PDF, find which accounting concept it represents.
This is the ONE function every parser calls instead of maintaining its
own hardcoded keyword dictionary.
"""

import sys, os
sys.path.append(os.path.dirname(__file__))
from concepts import CONCEPTS
from aliases import ALIASES


def match_label_to_concept(label_text, statement=None):
    """
    Given a raw text label from a PDF row, returns the matching concept
    name, or None if no alias matches. If `statement` is given, only
    concepts belonging to that statement are considered — this avoids,
    e.g., a balance sheet's "equity" false-matching an income statement
    row on a different page.
    """
    lower = label_text.lower().strip()

    for concept_name, alias_list in ALIASES.items():
        if statement:
            concept_statement = CONCEPTS.get(concept_name, {}).get("statement")
            if concept_statement != statement:
                continue
        if any(alias in lower for alias in alias_list):
            return concept_name

    return None


def concepts_for_statement(statement):
    """Returns all concept names belonging to a given statement."""
    return [name for name, meta in CONCEPTS.items() if meta["statement"] == statement]
